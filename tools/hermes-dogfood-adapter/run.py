from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in environments missing PyYAML
    yaml = None

from sync.checkpoint import CheckpointRecord, LocalCheckpointStore, checkpoint_from_message, is_message_after_checkpoint
from sync.hermes_reader import HermesMessage, HermesSession, fetch_all_messages, fetch_sessions, open_readonly_connection
from sync.mapper import MapperConfig, SessionMapContext, SessionMapResult, map_messages_for_session, map_session
from sync.purr_writer import PurrWriter, PurrWriterConfigurationError

DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
DEFAULT_POLL_INTERVAL_SECONDS = 30.0
DEFAULT_REQUIRED_SUPABASE_ENV = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
KILL_SWITCH_ENV = "PURR_SHADOW_ENABLED"
LOGGER_NAME = "hermes_dogfood_adapter"


@dataclass(frozen=True, slots=True)
class WriterSettings:
    timeout_seconds: float = 20.0
    batch_size: int = 200

    def __post_init__(self) -> None:
        if float(self.timeout_seconds) <= 0:
            raise ValueError(f"writer.timeout_seconds must be > 0, got {self.timeout_seconds!r}")
        if int(self.batch_size) <= 0:
            raise ValueError(f"writer.batch_size must be > 0, got {self.batch_size!r}")
        object.__setattr__(self, "timeout_seconds", float(self.timeout_seconds))
        object.__setattr__(self, "batch_size", int(self.batch_size))


@dataclass(frozen=True, slots=True)
class MapperSettings:
    pack_version: str = "phase0"
    default_source_provider: str = "hermes"
    default_surface: str = "other"

    def __post_init__(self) -> None:
        if not str(self.pack_version).strip():
            raise ValueError("mapper.pack_version must be non-empty")
        if not str(self.default_source_provider).strip():
            raise ValueError("mapper.default_source_provider must be non-empty")
        if not str(self.default_surface).strip():
            raise ValueError("mapper.default_surface must be non-empty")
        object.__setattr__(self, "pack_version", str(self.pack_version).strip())
        object.__setattr__(self, "default_source_provider", str(self.default_source_provider).strip())
        object.__setattr__(self, "default_surface", str(self.default_surface).strip())


@dataclass(frozen=True, slots=True)
class ShadowAdapterConfig:
    owner_id: str
    purr_id: str
    hermes_db_path: Path
    checkpoint_path: Path
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS
    log_dir: Path = Path("logs/dogfood")
    supabase_required_env: tuple[str, ...] = DEFAULT_REQUIRED_SUPABASE_ENV
    writer: WriterSettings = WriterSettings()
    mapper: MapperSettings = MapperSettings()

    def __post_init__(self) -> None:
        owner_id = str(self.owner_id).strip()
        purr_id = str(self.purr_id).strip()
        if not owner_id:
            raise ValueError("owner_id must be non-empty")
        if not purr_id:
            raise ValueError("purr_id must be non-empty")

        poll_interval = float(self.poll_interval)
        if poll_interval <= 0:
            raise ValueError(f"poll_interval must be > 0, got {self.poll_interval!r}")

        hermes_db_path = Path(self.hermes_db_path).expanduser()
        checkpoint_path = Path(self.checkpoint_path).expanduser()
        log_dir = Path(self.log_dir).expanduser()
        if not str(hermes_db_path):
            raise ValueError("hermes_db_path must be non-empty")
        if not str(checkpoint_path):
            raise ValueError("checkpoint_path must be non-empty")
        if not str(log_dir):
            raise ValueError("log_dir must be non-empty")

        required_env = tuple(str(item).strip() for item in self.supabase_required_env if str(item).strip())
        if not required_env:
            raise ValueError("supabase.required_env must contain at least one env var name")

        object.__setattr__(self, "owner_id", owner_id)
        object.__setattr__(self, "purr_id", purr_id)
        object.__setattr__(self, "poll_interval", poll_interval)
        object.__setattr__(self, "hermes_db_path", hermes_db_path)
        object.__setattr__(self, "checkpoint_path", checkpoint_path)
        object.__setattr__(self, "log_dir", log_dir)
        object.__setattr__(self, "supabase_required_env", required_env)

    def build_mapper_config(self) -> MapperConfig:
        return MapperConfig(
            owner_id=self.owner_id,
            purr_id=self.purr_id,
            pack_version=self.mapper.pack_version,
            default_source_provider=self.mapper.default_source_provider,
            default_surface=self.mapper.default_surface,
        )


@dataclass(frozen=True, slots=True)
class CycleStats:
    started_at: str
    duration_seconds: float
    sessions_seen: int
    total_messages_seen: int
    new_messages_seen: int
    mapped_sessions: int
    deferred_sessions: int
    deferred_messages: int
    episodes_written: int
    windows_written: int
    messages_written: int
    checkpoint_before: CheckpointRecord | None
    checkpoint_after: CheckpointRecord | None
    dry_run: bool = False


class ShadowAdapter:
    def __init__(
        self,
        config: ShadowAdapterConfig,
        *,
        writer: PurrWriter | None = None,
        dry_run: bool = False,
        logger: logging.Logger | None = None,
        sleep_fn: Any = time.sleep,
        time_fn: Any = time.perf_counter,
    ) -> None:
        self.config = config
        self.writer = writer
        self.dry_run = dry_run
        self.logger = logger or logging.getLogger(LOGGER_NAME)
        self.sleep_fn = sleep_fn
        self.time_fn = time_fn
        self.checkpoint_store = LocalCheckpointStore(config.checkpoint_path)
        self.mapper_config = config.build_mapper_config()

        if not self.dry_run and self.writer is None:
            raise ValueError("writer is required unless dry_run=True")

    def run_once(self) -> CycleStats:
        cycle_started_at = datetime.now(tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        started = self.time_fn()
        checkpoint_before = self.checkpoint_store.load()

        with closing(open_readonly_connection(self.config.hermes_db_path)) as connection:
            sessions = fetch_sessions(connection)
            messages = fetch_all_messages(connection)

        new_messages = [message for message in messages if is_message_after_checkpoint(message, checkpoint_before)]
        stats_kwargs: dict[str, Any] = {
            "started_at": cycle_started_at,
            "sessions_seen": len(sessions),
            "total_messages_seen": len(messages),
            "new_messages_seen": len(new_messages),
            "checkpoint_before": checkpoint_before,
            "dry_run": self.dry_run,
        }

        if not sessions:
            duration_seconds = self.time_fn() - started
            stats = CycleStats(
                duration_seconds=duration_seconds,
                mapped_sessions=0,
                deferred_sessions=0,
                deferred_messages=0,
                episodes_written=0,
                windows_written=0,
                messages_written=0,
                checkpoint_after=checkpoint_before,
                **stats_kwargs,
            )
            self._log_cycle_summary(stats, extra_message="empty Hermes DB or no sessions table yet")
            return stats

        if not new_messages:
            duration_seconds = self.time_fn() - started
            stats = CycleStats(
                duration_seconds=duration_seconds,
                mapped_sessions=0,
                deferred_sessions=0,
                deferred_messages=0,
                episodes_written=0,
                windows_written=0,
                messages_written=0,
                checkpoint_after=checkpoint_before,
                **stats_kwargs,
            )
            self._log_cycle_summary(stats, extra_message="no new messages after checkpoint")
            return stats

        sessions_by_id = {session.id: session for session in sessions}
        new_messages_by_session = _group_messages_by_session(new_messages)
        required_session_ids, processable_session_ids, missing_parent_by_session = _collect_required_session_ids(
            target_session_ids=new_messages_by_session.keys(),
            sessions_by_id=sessions_by_id,
        )

        mapped_results, mapped_order, unresolved_dependency_by_session = _map_sessions_in_dependency_order(
            required_session_ids=required_session_ids,
            sessions_by_id=sessions_by_id,
            mapper_config=self.mapper_config,
        )

        blocked_session_ids = set(missing_parent_by_session)
        blocked_session_ids.update(unresolved_dependency_by_session)
        blocked_session_ids.update(
            session_id for session_id in processable_session_ids if session_id not in mapped_results
        )
        processable_session_ids = {
            session_id for session_id in processable_session_ids if session_id in mapped_results and session_id not in blocked_session_ids
        }

        deferred_messages = sum(len(new_messages_by_session.get(session_id, ())) for session_id in blocked_session_ids)
        if missing_parent_by_session:
            details = ", ".join(
                f"{session_id}->{missing_parent_by_session[session_id]}"
                for session_id in sorted(missing_parent_by_session)
            )
            self.logger.warning("deferring child sessions with missing parents: %s", details)
        if unresolved_dependency_by_session:
            details = ", ".join(
                f"{session_id}->{unresolved_dependency_by_session[session_id] or 'unknown-parent'}"
                for session_id in sorted(unresolved_dependency_by_session)
            )
            self.logger.warning("deferring sessions with unresolved dependency order: %s", details)

        episode_rows = []
        window_rows = []
        for session_id in mapped_order:
            result = mapped_results[session_id]
            if result.episode is not None:
                episode_rows.append(result.episode)
            window_rows.append(result.window)

        message_rows = []
        processed_message_keys: set[tuple[str, str]] = set()
        for session_id in mapped_order:
            if session_id not in processable_session_ids:
                continue
            session_messages = new_messages_by_session.get(session_id, ())
            if not session_messages:
                continue
            mapped_messages = map_messages_for_session(
                session_messages,
                context=mapped_results[session_id].context,
                config=self.mapper_config,
            )
            message_rows.extend(mapped_messages)
            processed_message_keys.update(_source_message_key(message) for message in session_messages)

        episodes_written = 0
        windows_written = 0
        messages_written = 0
        if self.dry_run:
            episodes_written = len(episode_rows)
            windows_written = len(window_rows)
            messages_written = len(message_rows)
            self.logger.info(
                "dry-run: would write episodes=%s windows=%s messages=%s",
                episodes_written,
                windows_written,
                messages_written,
            )
        else:
            if episode_rows:
                episodes_written = self.writer.upsert_episodes(episode_rows).submitted
            if window_rows:
                windows_written = self.writer.upsert_session_windows(window_rows).submitted
            if message_rows:
                messages_written = self.writer.upsert_message_events(message_rows).submitted

        checkpoint_after = checkpoint_before
        if not self.dry_run:
            contiguous_checkpoint = _find_contiguous_checkpoint(
                ordered_messages=new_messages,
                processed_message_keys=processed_message_keys,
            )
            if contiguous_checkpoint is not None:
                checkpoint_after = self.checkpoint_store.advance(contiguous_checkpoint)

        duration_seconds = self.time_fn() - started
        stats = CycleStats(
            duration_seconds=duration_seconds,
            mapped_sessions=len(mapped_results),
            deferred_sessions=len(blocked_session_ids),
            deferred_messages=deferred_messages,
            episodes_written=episodes_written,
            windows_written=windows_written,
            messages_written=messages_written,
            checkpoint_after=checkpoint_after,
            **stats_kwargs,
        )
        self._log_cycle_summary(stats)
        return stats

    def run_forever(self) -> int:
        self.logger.info(
            "starting Hermes shadow adapter loop poll_interval=%ss dry_run=%s checkpoint=%s",
            self.config.poll_interval,
            self.dry_run,
            self.config.checkpoint_path,
        )
        while True:
            if not shadow_adapter_enabled():
                self.logger.info("%s=0 detected; stopping Hermes shadow adapter cleanly", KILL_SWITCH_ENV)
                return 0
            try:
                self.run_once()
            except Exception:
                self.logger.exception("adapter cycle failed")
            if not self._sleep_until_next_cycle(self.config.poll_interval):
                self.logger.info("%s=0 detected during sleep; stopping Hermes shadow adapter cleanly", KILL_SWITCH_ENV)
                return 0

    def _sleep_until_next_cycle(self, total_seconds: float) -> bool:
        remaining = max(0.0, float(total_seconds))
        while remaining > 0:
            if not shadow_adapter_enabled():
                return False
            chunk = min(1.0, remaining)
            self.sleep_fn(chunk)
            remaining -= chunk
        return shadow_adapter_enabled()

    def _log_cycle_summary(self, stats: CycleStats, *, extra_message: str | None = None) -> None:
        checkpoint_before = _format_checkpoint(stats.checkpoint_before)
        checkpoint_after = _format_checkpoint(stats.checkpoint_after)
        suffix = f" note={extra_message}" if extra_message else ""
        self.logger.info(
            "cycle complete started_at=%s duration_ms=%.1f sessions=%s total_messages=%s new_messages=%s mapped_sessions=%s deferred_sessions=%s deferred_messages=%s wrote_episodes=%s wrote_windows=%s wrote_messages=%s checkpoint_before=%s checkpoint_after=%s dry_run=%s%s",
            stats.started_at,
            stats.duration_seconds * 1000.0,
            stats.sessions_seen,
            stats.total_messages_seen,
            stats.new_messages_seen,
            stats.mapped_sessions,
            stats.deferred_sessions,
            stats.deferred_messages,
            stats.episodes_written,
            stats.windows_written,
            stats.messages_written,
            checkpoint_before,
            checkpoint_after,
            stats.dry_run,
            suffix,
        )


def load_config(path: str | Path) -> ShadowAdapterConfig:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load config.yaml for the Hermes shadow adapter")

    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise FileNotFoundError(f"Adapter config file does not exist: {config_path}")
    if not config_path.is_file():
        raise FileNotFoundError(f"Adapter config path is not a file: {config_path}")

    raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw_config is None:
        raw_config = {}
    if not isinstance(raw_config, Mapping):
        raise ValueError(f"Adapter config must contain a YAML mapping at top level: {config_path}")

    base_dir = config_path.parent
    writer_section = _as_mapping(raw_config.get("writer"), field_name="writer")
    mapper_section = _as_mapping(raw_config.get("mapper"), field_name="mapper")
    supabase_section = _as_mapping(raw_config.get("supabase"), field_name="supabase")

    return ShadowAdapterConfig(
        owner_id=_require_text(raw_config, "owner_id"),
        purr_id=_require_text(raw_config, "purr_id"),
        hermes_db_path=_resolve_config_path(_require_text(raw_config, "hermes_db_path"), base_dir=base_dir),
        checkpoint_path=_resolve_config_path(_require_text(raw_config, "checkpoint_path"), base_dir=base_dir),
        poll_interval=float(raw_config.get("poll_interval", DEFAULT_POLL_INTERVAL_SECONDS)),
        log_dir=_resolve_config_path(str(raw_config.get("log_dir", "logs/dogfood")), base_dir=base_dir),
        supabase_required_env=_parse_required_env(supabase_section.get("required_env", DEFAULT_REQUIRED_SUPABASE_ENV)),
        writer=WriterSettings(
            timeout_seconds=float(writer_section.get("timeout_seconds", 20.0)),
            batch_size=int(writer_section.get("batch_size", 200)),
        ),
        mapper=MapperSettings(
            pack_version=str(mapper_section.get("pack_version", "phase0")),
            default_source_provider=str(mapper_section.get("default_source_provider", "hermes")),
            default_surface=str(mapper_section.get("default_surface", "other")),
        ),
    )


def configure_logging(log_dir: Path, *, logger_name: str = LOGGER_NAME) -> logging.Logger:
    log_dir = Path(log_dir).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"adapter-{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger


def build_writer_from_env(config: ShadowAdapterConfig) -> PurrWriter:
    missing_env = [name for name in config.supabase_required_env if not os.environ.get(name, "").strip()]
    if missing_env:
        raise PurrWriterConfigurationError(
            "Missing required Supabase environment variables for Hermes shadow adapter: "
            + ", ".join(missing_env)
        )
    return PurrWriter.from_env(
        timeout_seconds=config.writer.timeout_seconds,
        batch_size=config.writer.batch_size,
    )


def shadow_adapter_enabled() -> bool:
    raw_value = os.environ.get(KILL_SWITCH_ENV)
    if raw_value is None:
        return True
    return str(raw_value).strip().lower() not in {"0", "false", "off", "no"}


def _group_messages_by_session(messages: Sequence[HermesMessage]) -> dict[str, list[HermesMessage]]:
    grouped: dict[str, list[HermesMessage]] = defaultdict(list)
    for message in messages:
        grouped[message.session_id].append(message)
    return grouped


def _collect_required_session_ids(
    *,
    target_session_ids: Sequence[str] | Any,
    sessions_by_id: Mapping[str, HermesSession],
) -> tuple[set[str], set[str], dict[str, str]]:
    required_session_ids: set[str] = set()
    processable_session_ids: set[str] = set()
    missing_parent_by_session: dict[str, str] = {}

    for session_id in sorted(set(str(item) for item in target_session_ids)):
        lineage: list[str] = []
        current_session_id: str | None = session_id
        seen: set[str] = set()
        missing_parent_id: str | None = None
        while current_session_id is not None:
            if current_session_id in seen:
                missing_parent_id = current_session_id
                break
            seen.add(current_session_id)
            session = sessions_by_id.get(current_session_id)
            if session is None:
                missing_parent_id = current_session_id
                break
            lineage.append(current_session_id)
            current_session_id = session.parent_session_id

        if missing_parent_id is not None:
            missing_parent_by_session[session_id] = missing_parent_id
            continue

        required_session_ids.update(lineage)
        processable_session_ids.add(session_id)

    return required_session_ids, processable_session_ids, missing_parent_by_session


def _map_sessions_in_dependency_order(
    *,
    required_session_ids: set[str],
    sessions_by_id: Mapping[str, HermesSession],
    mapper_config: MapperConfig,
) -> tuple[dict[str, SessionMapResult], list[str], dict[str, str | None]]:
    pending = sorted(
        [sessions_by_id[session_id] for session_id in required_session_ids],
        key=lambda session: (float(session.started_at), session.id),
    )
    mapped_results: dict[str, SessionMapResult] = {}
    mapped_order: list[str] = []

    while pending:
        progress = False
        next_pending: list[HermesSession] = []
        for session in pending:
            parent_session_id = session.parent_session_id
            parent_context: SessionMapContext | None = None
            if parent_session_id is not None:
                parent_result = mapped_results.get(parent_session_id)
                if parent_result is None:
                    next_pending.append(session)
                    continue
                parent_context = parent_result.context

            mapped = map_session(session, config=mapper_config, parent_context=parent_context)
            mapped_results[session.id] = mapped
            mapped_order.append(session.id)
            progress = True

        if progress:
            pending = next_pending
            continue

        unresolved = {session.id: session.parent_session_id for session in pending}
        return mapped_results, mapped_order, unresolved

    return mapped_results, mapped_order, {}


def _find_contiguous_checkpoint(
    *,
    ordered_messages: Sequence[HermesMessage],
    processed_message_keys: set[tuple[str, str]],
) -> CheckpointRecord | None:
    latest: CheckpointRecord | None = None
    for message in ordered_messages:
        if _source_message_key(message) not in processed_message_keys:
            break
        latest = checkpoint_from_message(message)
    return latest


def _source_message_key(message: HermesMessage) -> tuple[str, str]:
    return (str(message.session_id), str(message.id))


def _parse_required_env(value: Any) -> tuple[str, ...]:
    if value is None:
        return DEFAULT_REQUIRED_SUPABASE_ENV
    if isinstance(value, str):
        parts = [item.strip() for item in value.split(",")]
        required_env = tuple(item for item in parts if item)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        required_env = tuple(str(item).strip() for item in value if str(item).strip())
    else:
        raise ValueError("supabase.required_env must be a string or list of env var names")
    if not required_env:
        raise ValueError("supabase.required_env must not be empty")
    return required_env


def _resolve_config_path(value: str, *, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _as_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping if provided")
    return value


def _require_text(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{field_name} is required in adapter config")
    return text


def _format_checkpoint(checkpoint: CheckpointRecord | None) -> str:
    if checkpoint is None:
        return "none"
    return f"{checkpoint.timestamp}:{checkpoint.message_id}:{checkpoint.session_id or '-'}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hermes phase-0 shadow adapter")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="path to adapter config.yaml")
    parser.add_argument("--once", action="store_true", help="run exactly one poll cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="map and log but skip Supabase writes/checkpoint updates")
    args = parser.parse_args(argv)

    if not shadow_adapter_enabled():
        print(f"{KILL_SWITCH_ENV}=0 detected; Hermes shadow adapter disabled, exiting cleanly.")
        return 0

    try:
        config = load_config(args.config)
        logger = configure_logging(config.log_dir)
        writer = None if args.dry_run else build_writer_from_env(config)
        adapter = ShadowAdapter(config, writer=writer, dry_run=args.dry_run, logger=logger)
        if args.once:
            adapter.run_once()
            return 0
        return adapter.run_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received; Hermes shadow adapter stopped cleanly.")
        return 0
    except Exception as exc:
        print(f"Hermes shadow adapter failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
