from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence, TypedDict
from uuid import UUID, uuid5

from .hermes_reader import HermesMessage, HermesSession


HERMES_PURR_NAMESPACE = UUID("77886d8f-9664-5aca-a504-7ac2939fc378")
_SOURCE_PROVIDER_PREFIX = "hermes"
_ROLE_MAP = {
    "user": "user",
    "assistant": "purr",
    "system": "system",
    "tool": "system",
}
_SURFACE_MAP = {
    "telegram": "world_chat",
}


class EpisodeRow(TypedDict):
    episode_id: str
    owner_id: str
    purr_id: str
    kind: str
    status: str
    parent_episode_id: str | None
    started_at: str
    ended_at: str | None
    metadata_json: dict[str, Any]


class SessionWindowRow(TypedDict):
    window_id: str
    owner_id: str
    purr_id: str
    episode_id: str
    parent_window_id: str | None
    source_provider: str
    source_session_id: str
    entry_surface: str
    window_state: str
    opened_at: str
    closed_at: str | None
    closure_reason: str | None
    pack_version: str
    metadata_json: dict[str, Any]


class MessageEventRow(TypedDict):
    message_id: str
    owner_id: str
    purr_id: str
    episode_id: str
    window_id: str
    source_provider: str
    source_message_id: str
    role: str
    surface: str
    tool_visibility: str
    content_text: str
    metadata_json: dict[str, Any]
    reply_to_message_id: str | None
    created_at: str


@dataclass(frozen=True, slots=True)
class MapperConfig:
    owner_id: str | UUID
    purr_id: str | UUID
    namespace: str | UUID = HERMES_PURR_NAMESPACE
    default_source_provider: str = _SOURCE_PROVIDER_PREFIX
    default_surface: str = "other"
    pack_version: str = "phase0"

    def __post_init__(self) -> None:
        object.__setattr__(self, "owner_id", str(UUID(str(self.owner_id))))
        object.__setattr__(self, "purr_id", str(UUID(str(self.purr_id))))
        object.__setattr__(self, "namespace", UUID(str(self.namespace)))

        if not self.default_source_provider.strip():
            raise ValueError("default_source_provider must be non-empty")
        if not self.default_surface.strip():
            raise ValueError("default_surface must be non-empty")
        if not self.pack_version.strip():
            raise ValueError("pack_version must be non-empty")


@dataclass(frozen=True, slots=True)
class SessionMapContext:
    owner_id: str
    purr_id: str
    episode_id: str
    episode_started_at: str
    window_id: str
    parent_window_id: str | None
    source_provider: str
    surface: str
    source_session_id: str


@dataclass(frozen=True, slots=True)
class SessionMapResult:
    context: SessionMapContext
    episode: EpisodeRow | None
    window: SessionWindowRow


@dataclass(frozen=True, slots=True)
class SessionBundleMapResult:
    context: SessionMapContext
    episode: EpisodeRow | None
    window: SessionWindowRow
    messages: list[MessageEventRow]


HermesSessionLike = HermesSession | Mapping[str, Any]
HermesMessageLike = HermesMessage | Mapping[str, Any]


def make_episode_id(session_id: str, *, namespace: UUID = HERMES_PURR_NAMESPACE) -> str:
    return str(uuid5(namespace, f"hermes.episode.{session_id}"))


def make_window_id(session_id: str, *, namespace: UUID = HERMES_PURR_NAMESPACE) -> str:
    return str(uuid5(namespace, f"hermes.window.{session_id}"))


def make_message_id(
    session_id: str,
    message_id: int | str,
    *,
    namespace: UUID = HERMES_PURR_NAMESPACE,
) -> str:
    return str(uuid5(namespace, f"hermes.msg.{session_id}.{message_id}"))


def map_session(
    session: HermesSessionLike,
    *,
    config: MapperConfig,
    parent_context: SessionMapContext | None = None,
) -> SessionMapResult:
    source_session_id = _as_text(_get_field(session, "id"), field_name="id")
    parent_session_id = _optional_text(_get_field(session, "parent_session_id"))
    source_provider = map_source_provider(_optional_text(_get_field(session, "source")), config=config)
    surface = map_surface(_optional_text(_get_field(session, "source")), config=config)

    if parent_session_id is None:
        episode_id = make_episode_id(source_session_id, namespace=config.namespace)
        episode_started_at = _require_timestamptz(_get_field(session, "started_at"), field_name="started_at")
        parent_window_id = None
        emit_episode = True
    else:
        if parent_context is None:
            raise ValueError(
                f"Child Hermes session {source_session_id!r} requires parent_context for parent_session_id={parent_session_id!r}"
            )
        if (
            parent_context.source_session_id
            and parent_context.source_session_id != parent_session_id
        ):
            raise ValueError(
                "parent_context.source_session_id does not match Hermes parent_session_id: "
                f"{parent_context.source_session_id!r} != {parent_session_id!r}"
            )
        if parent_context.owner_id != config.owner_id or parent_context.purr_id != config.purr_id:
            raise ValueError(
                "parent_context identity does not match mapper config: "
                f"({parent_context.owner_id!r}, {parent_context.purr_id!r}) != "
                f"({config.owner_id!r}, {config.purr_id!r})"
            )
        episode_id = parent_context.episode_id
        episode_started_at = parent_context.episode_started_at
        parent_window_id = parent_context.window_id
        emit_episode = False

    window_id = make_window_id(source_session_id, namespace=config.namespace)
    context = SessionMapContext(
        owner_id=config.owner_id,
        purr_id=config.purr_id,
        episode_id=episode_id,
        episode_started_at=episode_started_at,
        window_id=window_id,
        parent_window_id=parent_window_id,
        source_provider=source_provider,
        surface=surface,
        source_session_id=source_session_id,
    )
    episode = (
        _build_episode_row(
            session,
            config=config,
            context=context,
        )
        if emit_episode
        else None
    )
    window = _build_window_row(
        session,
        config=config,
        context=context,
    )
    return SessionMapResult(context=context, episode=episode, window=window)


def map_message(
    message: HermesMessageLike,
    *,
    context: SessionMapContext,
    config: MapperConfig,
) -> MessageEventRow:
    source_message_id = _as_text(_get_field(message, "id"), field_name="id")
    source_session_id = _as_text(_get_field(message, "session_id"), field_name="session_id")
    if source_session_id != context.source_session_id:
        raise ValueError(
            f"Message session_id {source_session_id!r} does not match mapped session {context.source_session_id!r}"
        )

    tool_name = _optional_text(_get_field(message, "tool_name"))
    raw_role = _optional_text(_get_field(message, "role"))
    role = map_message_role(raw_role)
    raw_content = _get_field(message, "content")
    content_text = "" if raw_content is None else str(raw_content)

    metadata_json = _compact_dict(
        {
            "hermes_role": raw_role,
            "tool_call_id": _optional_text(_get_field(message, "tool_call_id")),
            "tool_name": tool_name,
            "tool_calls": _get_field(message, "tool_calls"),
            "tool_calls_raw": _optional_text(_get_field(message, "tool_calls_raw")),
            "token_count": _get_field(message, "token_count"),
            "finish_reason": _optional_text(_get_field(message, "finish_reason")),
        }
    )

    return {
        "message_id": make_message_id(
            context.source_session_id,
            source_message_id,
            namespace=config.namespace,
        ),
        "owner_id": context.owner_id,
        "purr_id": context.purr_id,
        "episode_id": context.episode_id,
        "window_id": context.window_id,
        "source_provider": context.source_provider,
        "source_message_id": source_message_id,
        "role": role,
        "surface": context.surface,
        "tool_visibility": "hidden" if tool_name is not None else "none",
        "content_text": content_text,
        "metadata_json": metadata_json,
        "reply_to_message_id": None,
        "created_at": _require_timestamptz(_get_field(message, "timestamp"), field_name="timestamp"),
    }


def map_messages_for_session(
    messages: Sequence[HermesMessageLike],
    *,
    context: SessionMapContext,
    config: MapperConfig,
) -> list[MessageEventRow]:
    ordered_messages = sorted(messages, key=_message_sort_key)
    return [map_message(message, context=context, config=config) for message in ordered_messages]


def map_session_bundle(
    session: HermesSessionLike,
    messages: Sequence[HermesMessageLike],
    *,
    config: MapperConfig,
    parent_context: SessionMapContext | None = None,
) -> SessionBundleMapResult:
    session_rows = map_session(session, config=config, parent_context=parent_context)
    return SessionBundleMapResult(
        context=session_rows.context,
        episode=session_rows.episode,
        window=session_rows.window,
        messages=map_messages_for_session(messages, context=session_rows.context, config=config),
    )


def map_message_role(role: str | None) -> str:
    if role is None:
        raise ValueError("role must be present")
    normalized = role.lower()
    if normalized not in _ROLE_MAP:
        raise ValueError(f"Unsupported Hermes message role: {role!r}")
    return _ROLE_MAP[normalized]


def map_surface(source: str | None, *, config: MapperConfig) -> str:
    if source is None:
        return config.default_surface
    return _SURFACE_MAP.get(source.lower(), config.default_surface)


def map_source_provider(source: str | None, *, config: MapperConfig) -> str:
    # Keep provider identity stable for the shadow adapter; transport/source details
    # belong in surface + metadata, not in the provider key itself.
    return config.default_source_provider


def unix_to_timestamptz(value: float | int | str | None) -> str | None:
    if value is None:
        return None
    timestamp = float(value)
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _require_timestamptz(value: float | int | str | None, *, field_name: str) -> str:
    timestamp = unix_to_timestamptz(value)
    if timestamp is None:
        raise ValueError(f"{field_name} must be present")
    return timestamp


def _build_episode_row(
    session: HermesSessionLike,
    *,
    config: MapperConfig,
    context: SessionMapContext,
) -> EpisodeRow:
    raw_ended_at = unix_to_timestamptz(_get_field(session, "ended_at"))
    end_reason = _optional_text(_get_field(session, "end_reason"))
    status = "open" if end_reason == "compression" or raw_ended_at is None else "closed"
    ended_at = None if end_reason == "compression" else raw_ended_at
    metadata_json = _compact_dict(
        {
            "source_provider": context.source_provider,
            "source_session_id": context.source_session_id,
            "source": _optional_text(_get_field(session, "source")),
            "entry_surface": context.surface,
            "hermes_user_id": _optional_text(_get_field(session, "user_id")),
            "model": _optional_text(_get_field(session, "model")),
            "model_config": _get_field(session, "model_config"),
            "model_config_raw": _optional_text(_get_field(session, "model_config_raw")),
            "system_prompt": _optional_text(_get_field(session, "system_prompt")),
            "title": _optional_text(_get_field(session, "title")),
            "end_reason": end_reason,
            "message_count": _get_field(session, "message_count"),
            "tool_call_count": _get_field(session, "tool_call_count"),
            "input_tokens": _get_field(session, "input_tokens"),
            "output_tokens": _get_field(session, "output_tokens"),
        }
    )
    return {
        "episode_id": context.episode_id,
        "owner_id": config.owner_id,
        "purr_id": config.purr_id,
        "kind": "daily_chat",
        "status": status,
        "parent_episode_id": None,
        "started_at": context.episode_started_at,
        "ended_at": ended_at,
        "metadata_json": metadata_json,
    }


def _build_window_row(
    session: HermesSessionLike,
    *,
    config: MapperConfig,
    context: SessionMapContext,
) -> SessionWindowRow:
    end_reason = _optional_text(_get_field(session, "end_reason"))
    metadata_json = _compact_dict(
        {
            "source": _optional_text(_get_field(session, "source")),
            "hermes_user_id": _optional_text(_get_field(session, "user_id")),
            "model": _optional_text(_get_field(session, "model")),
            "model_config": _get_field(session, "model_config"),
            "model_config_raw": _optional_text(_get_field(session, "model_config_raw")),
            "system_prompt": _optional_text(_get_field(session, "system_prompt")),
            "title": _optional_text(_get_field(session, "title")),
            "parent_session_id": _optional_text(_get_field(session, "parent_session_id")),
            "message_count": _get_field(session, "message_count"),
            "tool_call_count": _get_field(session, "tool_call_count"),
            "input_tokens": _get_field(session, "input_tokens"),
            "output_tokens": _get_field(session, "output_tokens"),
        }
    )
    return {
        "window_id": context.window_id,
        "owner_id": context.owner_id,
        "purr_id": context.purr_id,
        "episode_id": context.episode_id,
        "parent_window_id": context.parent_window_id,
        "source_provider": context.source_provider,
        "source_session_id": context.source_session_id,
        "entry_surface": context.surface,
        "window_state": _map_window_state(
            ended_at=_get_field(session, "ended_at"),
            end_reason=end_reason,
        ),
        "opened_at": _require_timestamptz(_get_field(session, "started_at"), field_name="started_at"),
        "closed_at": unix_to_timestamptz(_get_field(session, "ended_at")),
        "closure_reason": end_reason,
        "pack_version": config.pack_version,
        "metadata_json": metadata_json,
    }


def _map_window_state(*, ended_at: Any, end_reason: str | None) -> str:
    if end_reason == "compression":
        return "compressed"
    if ended_at is not None:
        return "archived"
    return "active"


def _get_field(item: HermesSessionLike | HermesMessageLike, field_name: str) -> Any:
    if isinstance(item, Mapping):
        return item.get(field_name)
    return getattr(item, field_name, None)


def _message_sort_key(message: HermesMessageLike) -> tuple[float, int, int | str]:
    message_id = _as_text(_get_field(message, "id"), field_name="id")
    if message_id.isdigit():
        return (float(_get_field(message, "timestamp")), 0, int(message_id))
    return (float(_get_field(message, "timestamp")), 1, message_id)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_text(value: Any, *, field_name: str) -> str:
    text = _optional_text(value)
    if text is None:
        raise ValueError(f"{field_name} must be present")
    return text


def _compact_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {}
    for key, value in payload.items():
        if value is None:
            continue
        compacted[key] = value
    return compacted


__all__ = [
    "EpisodeRow",
    "HERMES_PURR_NAMESPACE",
    "MapperConfig",
    "MessageEventRow",
    "SessionBundleMapResult",
    "SessionMapContext",
    "SessionMapResult",
    "SessionWindowRow",
    "make_episode_id",
    "make_message_id",
    "make_window_id",
    "map_message",
    "map_message_role",
    "map_messages_for_session",
    "map_session",
    "map_session_bundle",
    "map_source_provider",
    "map_surface",
    "unix_to_timestamptz",
]
