from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class HermesReaderError(RuntimeError):
    """Raised when the Hermes SQLite reader cannot open or read the database."""


@dataclass(frozen=True, slots=True)
class HermesSession:
    id: str
    source: str
    user_id: str | None
    model: str | None
    model_config: Any | None
    model_config_raw: str | None
    system_prompt: str | None
    parent_session_id: str | None
    started_at: float
    ended_at: float | None
    end_reason: str | None
    message_count: int
    tool_call_count: int
    input_tokens: int
    output_tokens: int
    title: str | None


@dataclass(frozen=True, slots=True)
class HermesMessage:
    id: int
    session_id: str
    role: str
    content: str | None
    tool_call_id: str | None
    tool_calls: Any | None
    tool_calls_raw: str | None
    tool_name: str | None
    timestamp: float
    token_count: int | None
    finish_reason: str | None


SESSION_COLUMNS = (
    "id",
    "source",
    "user_id",
    "model",
    "model_config",
    "system_prompt",
    "parent_session_id",
    "started_at",
    "ended_at",
    "end_reason",
    "message_count",
    "tool_call_count",
    "input_tokens",
    "output_tokens",
    "title",
)

MESSAGE_COLUMNS = (
    "id",
    "session_id",
    "role",
    "content",
    "tool_call_id",
    "tool_calls",
    "tool_name",
    "timestamp",
    "token_count",
    "finish_reason",
)


def open_readonly_connection(db_path: str | Path, *, timeout: float = 5.0) -> sqlite3.Connection:
    """Open a Hermes SQLite database in read-only/query-only mode.

    Raises FileNotFoundError with a clear message when the file is missing.
    Raises HermesReaderError when SQLite cannot open the database.
    """

    path = Path(db_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Hermes SQLite database does not exist: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Hermes SQLite database path is not a file: {path}")

    resolved = path.resolve()
    uri = f"{resolved.as_uri()}?mode=ro"

    try:
        connection = sqlite3.connect(uri, uri=True, timeout=timeout)
    except sqlite3.Error as exc:
        raise HermesReaderError(f"Failed to open Hermes SQLite database read-only: {resolved}") from exc

    connection.row_factory = sqlite3.Row
    connection.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
    connection.execute("PRAGMA query_only = ON")
    return connection


def fetch_sessions(
    connection: sqlite3.Connection,
    *,
    limit: int | None = None,
    offset: int = 0,
) -> list[HermesSession]:
    """Fetch Hermes sessions ordered stably by started_at, id.

    If the database has no sessions table yet, returns an empty list.
    """

    _validate_pagination(limit=limit, offset=offset)
    if not _table_exists(connection, "sessions"):
        return []
    _require_columns(connection, "sessions", SESSION_COLUMNS)

    query = (
        f"SELECT {', '.join(SESSION_COLUMNS)} "
        "FROM sessions "
        "ORDER BY started_at ASC, id ASC"
    )
    params: list[Any] = []
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    elif offset:
        query += " LIMIT -1 OFFSET ?"
        params.append(offset)

    try:
        rows = connection.execute(query, params).fetchall()
    except sqlite3.Error as exc:
        raise HermesReaderError("Failed to read Hermes sessions from SQLite database") from exc
    return [_row_to_session(row) for row in rows]


def fetch_messages_for_session(
    connection: sqlite3.Connection,
    session_id: str,
) -> list[HermesMessage]:
    """Fetch all messages for one Hermes session ordered by timestamp, id.

    Missing messages table or unknown session_id both return an empty list.
    """

    if not _table_exists(connection, "messages"):
        return []
    _require_columns(connection, "messages", MESSAGE_COLUMNS)

    try:
        rows = connection.execute(
            f"SELECT {', '.join(MESSAGE_COLUMNS)} "
            "FROM messages "
            "WHERE session_id = ? "
            "ORDER BY timestamp ASC, id ASC",
            (session_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        raise HermesReaderError(
            f"Failed to read Hermes messages for session {session_id!r} from SQLite database"
        ) from exc
    return [_row_to_message(row) for row in rows]


def fetch_all_messages(
    connection: sqlite3.Connection,
    *,
    limit: int | None = None,
    offset: int = 0,
) -> list[HermesMessage]:
    """Fetch all Hermes messages ordered stably by timestamp, id."""

    _validate_pagination(limit=limit, offset=offset)
    if not _table_exists(connection, "messages"):
        return []
    _require_columns(connection, "messages", MESSAGE_COLUMNS)

    query = (
        f"SELECT {', '.join(MESSAGE_COLUMNS)} "
        "FROM messages "
        "ORDER BY timestamp ASC, id ASC"
    )
    params: list[Any] = []
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    elif offset:
        query += " LIMIT -1 OFFSET ?"
        params.append(offset)

    try:
        rows = connection.execute(query, params).fetchall()
    except sqlite3.Error as exc:
        raise HermesReaderError("Failed to read Hermes messages from SQLite database") from exc
    return [_row_to_message(row) for row in rows]


def _row_to_session(row: sqlite3.Row) -> HermesSession:
    raw_model_config = row["model_config"]
    return HermesSession(
        id=row["id"],
        source=row["source"],
        user_id=row["user_id"],
        model=row["model"],
        model_config=_decode_json(raw_model_config),
        model_config_raw=raw_model_config,
        system_prompt=row["system_prompt"],
        parent_session_id=row["parent_session_id"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        end_reason=row["end_reason"],
        message_count=row["message_count"] or 0,
        tool_call_count=row["tool_call_count"] or 0,
        input_tokens=row["input_tokens"] or 0,
        output_tokens=row["output_tokens"] or 0,
        title=row["title"],
    )


def _row_to_message(row: sqlite3.Row) -> HermesMessage:
    raw_tool_calls = row["tool_calls"]
    return HermesMessage(
        id=row["id"],
        session_id=row["session_id"],
        role=row["role"],
        content=row["content"],
        tool_call_id=row["tool_call_id"],
        tool_calls=_decode_json(raw_tool_calls),
        tool_calls_raw=raw_tool_calls,
        tool_name=row["tool_name"],
        timestamp=row["timestamp"],
        token_count=row["token_count"],
        finish_reason=row["finish_reason"],
    )


def _decode_json(raw_value: str | None) -> Any | None:
    if raw_value in (None, ""):
        return None

    try:
        return json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
        return None


def _validate_pagination(*, limit: int | None, offset: int) -> None:
    if limit is not None and limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")
    if offset < 0:
        raise ValueError(f"offset must be >= 0, got {offset}")


def _require_columns(
    connection: sqlite3.Connection,
    table_name: str,
    expected_columns: tuple[str, ...],
) -> None:
    try:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    except sqlite3.Error as exc:
        raise HermesReaderError(f"Failed to inspect Hermes SQLite schema for table {table_name!r}") from exc

    actual_columns = {row["name"] for row in rows}
    missing = [column for column in expected_columns if column not in actual_columns]
    if missing:
        raise HermesReaderError(
            f"Hermes SQLite table {table_name!r} is missing expected columns: {', '.join(missing)}"
        )



def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    try:
        row = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ? LIMIT 1",
            (table_name,),
        ).fetchone()
    except sqlite3.Error as exc:
        raise HermesReaderError(f"Failed to inspect Hermes SQLite table list for {table_name!r}") from exc
    return row is not None
