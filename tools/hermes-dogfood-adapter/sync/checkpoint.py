from __future__ import annotations

import json
import math
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import fcntl

from .hermes_reader import HermesMessage

CHECKPOINT_SCHEMA_VERSION = 1


class CheckpointError(RuntimeError):
    """Base error for Hermes adapter checkpoint persistence."""


class CheckpointFormatError(CheckpointError):
    """Raised when a checkpoint file exists but cannot be parsed safely."""


HermesMessageLike = HermesMessage | Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    """Stable cursor for the last fully processed Hermes message.

    Ordering is defined by Hermes message timestamp, then Hermes message id.
    session_id is stored for observability and validation context but is not part
    of the ordering cursor because Hermes reads are already ordered by
    `(timestamp, id)`.
    """

    timestamp: float
    message_id: str
    session_id: str | None = None
    schema_version: int = CHECKPOINT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            normalized_timestamp = float(self.timestamp)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"timestamp must be a real number, got {self.timestamp!r}") from exc
        if not math.isfinite(normalized_timestamp):
            raise ValueError(f"timestamp must be finite, got {self.timestamp!r}")

        normalized_message_id = str(self.message_id).strip()
        if not normalized_message_id:
            raise ValueError("message_id must be non-empty")

        normalized_session_id = None
        if self.session_id is not None:
            session_text = str(self.session_id).strip()
            normalized_session_id = session_text or None

        normalized_schema_version = int(self.schema_version)
        if normalized_schema_version != CHECKPOINT_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported checkpoint schema_version {self.schema_version!r}; "
                f"expected {CHECKPOINT_SCHEMA_VERSION}"
            )

        object.__setattr__(self, "timestamp", normalized_timestamp)
        object.__setattr__(self, "message_id", normalized_message_id)
        object.__setattr__(self, "session_id", normalized_session_id)
        object.__setattr__(self, "schema_version", normalized_schema_version)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "last_processed_timestamp": self.timestamp,
            "last_processed_message_id": self.message_id,
        }
        if self.session_id is not None:
            payload["last_processed_session_id"] = self.session_id
        return payload


class LocalCheckpointStore:
    """Crash-safe local checkpoint store backed by one JSON file.

    A best-effort advisory file lock is used so multiple adapter processes do not
    race load/advance/save and regress the checkpoint cursor.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).expanduser()
        self._lock_path = self._path.with_name(f"{self._path.name}.lock")

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> CheckpointRecord | None:
        with _exclusive_lock(self._lock_path):
            return load_checkpoint(self._path)

    def save(self, checkpoint: CheckpointRecord) -> CheckpointRecord:
        with _exclusive_lock(self._lock_path):
            return save_checkpoint(self._path, checkpoint)

    def advance(self, checkpoint: CheckpointRecord | None) -> CheckpointRecord | None:
        with _exclusive_lock(self._lock_path):
            current = load_checkpoint(self._path)
            advanced = advance_checkpoint(current, checkpoint)
            if advanced is not None and advanced != current:
                save_checkpoint(self._path, advanced)
            return advanced


def load_checkpoint(path: str | Path) -> CheckpointRecord | None:
    checkpoint_path = Path(path).expanduser()
    if not checkpoint_path.exists():
        return None
    if not checkpoint_path.is_file():
        raise CheckpointFormatError(f"Checkpoint path is not a file: {checkpoint_path}")

    try:
        raw_payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CheckpointError(f"Failed to read checkpoint file: {checkpoint_path}") from exc
    except json.JSONDecodeError as exc:
        raise CheckpointFormatError(f"Invalid checkpoint JSON in {checkpoint_path}: {exc.msg}") from exc

    return _parse_checkpoint_payload(raw_payload, path=checkpoint_path)


def save_checkpoint(path: str | Path, checkpoint: CheckpointRecord) -> CheckpointRecord:
    checkpoint_path = Path(path).expanduser()
    try:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise CheckpointError(f"Failed to prepare checkpoint directory: {checkpoint_path.parent}") from exc
    payload = checkpoint.to_dict()

    temp_path: Path | None = None
    try:
        fd, raw_temp_path = tempfile.mkstemp(
            prefix=f".{checkpoint_path.name}.",
            suffix=".tmp",
            dir=str(checkpoint_path.parent),
        )
        temp_path = Path(raw_temp_path)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, checkpoint_path)
        _fsync_directory(checkpoint_path.parent)
    except OSError as exc:
        raise CheckpointError(f"Failed to write checkpoint file atomically: {checkpoint_path}") from exc
    finally:
        if temp_path is not None and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass

    return checkpoint


def checkpoint_from_message(message: HermesMessageLike) -> CheckpointRecord:
    return CheckpointRecord(
        timestamp=_get_required_float(message, field_name="timestamp"),
        message_id=_get_required_text(message, field_name="id"),
        session_id=_optional_text(_get_field(message, "session_id")),
    )


def checkpoint_for_batch(messages: Iterable[HermesMessageLike]) -> CheckpointRecord | None:
    return max_checkpoint(checkpoint_from_message(message) for message in messages)


def max_checkpoint(checkpoints: Iterable[CheckpointRecord | None]) -> CheckpointRecord | None:
    latest: CheckpointRecord | None = None
    for checkpoint in checkpoints:
        latest = advance_checkpoint(latest, checkpoint)
    return latest


def advance_checkpoint(
    current: CheckpointRecord | None,
    candidate: CheckpointRecord | None,
) -> CheckpointRecord | None:
    if candidate is None:
        return current
    if current is None:
        return candidate
    if compare_checkpoints(candidate, current) > 0:
        return candidate
    return current


def is_message_after_checkpoint(
    message: HermesMessageLike,
    checkpoint: CheckpointRecord | None,
) -> bool:
    if checkpoint is None:
        return True
    return compare_checkpoints(checkpoint_from_message(message), checkpoint) > 0


def compare_checkpoints(left: CheckpointRecord, right: CheckpointRecord) -> int:
    if left.timestamp < right.timestamp:
        return -1
    if left.timestamp > right.timestamp:
        return 1

    left_message_key = _message_id_sort_key(left.message_id)
    right_message_key = _message_id_sort_key(right.message_id)
    if left_message_key < right_message_key:
        return -1
    if left_message_key > right_message_key:
        return 1
    return 0


def _parse_checkpoint_payload(raw_payload: Any, *, path: Path) -> CheckpointRecord:
    if not isinstance(raw_payload, Mapping):
        raise CheckpointFormatError(f"Checkpoint file {path} must contain a JSON object")

    schema_version = raw_payload.get("schema_version")
    if schema_version is None:
        raise CheckpointFormatError(f"Checkpoint file {path} is missing required field 'schema_version'")

    try:
        return CheckpointRecord(
            timestamp=raw_payload["last_processed_timestamp"],
            message_id=raw_payload["last_processed_message_id"],
            session_id=raw_payload.get("last_processed_session_id"),
            schema_version=schema_version,
        )
    except KeyError as exc:
        raise CheckpointFormatError(
            f"Checkpoint file {path} is missing required field {exc.args[0]!r}"
        ) from exc
    except ValueError as exc:
        raise CheckpointFormatError(f"Checkpoint file {path} is invalid: {exc}") from exc


def _fsync_directory(path: Path) -> None:
    try:
        directory_fd = os.open(path, os.O_RDONLY)
    except OSError as exc:
        raise CheckpointError(f"Failed to open checkpoint directory for fsync: {path}") from exc

    try:
        os.fsync(directory_fd)
    except OSError as exc:
        raise CheckpointError(f"Failed to fsync checkpoint directory: {path}") from exc
    finally:
        os.close(directory_fd)


@contextmanager
def _exclusive_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def _get_field(message: HermesMessageLike, field_name: str) -> Any:
    if isinstance(message, Mapping):
        return message.get(field_name)
    return getattr(message, field_name, None)


def _get_required_float(message: HermesMessageLike, *, field_name: str) -> float:
    value = _get_field(message, field_name)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a real number, got {value!r}") from exc


def _get_required_text(message: HermesMessageLike, *, field_name: str) -> str:
    value = _optional_text(_get_field(message, field_name))
    if value is None:
        raise ValueError(f"{field_name} must be present")
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _message_id_sort_key(message_id: str) -> tuple[int, int | str]:
    if message_id.isdigit():
        return (0, int(message_id))
    return (1, message_id)


__all__ = [
    "CHECKPOINT_SCHEMA_VERSION",
    "CheckpointError",
    "CheckpointFormatError",
    "CheckpointRecord",
    "LocalCheckpointStore",
    "advance_checkpoint",
    "checkpoint_for_batch",
    "checkpoint_from_message",
    "compare_checkpoints",
    "is_message_after_checkpoint",
    "load_checkpoint",
    "max_checkpoint",
    "save_checkpoint",
]
