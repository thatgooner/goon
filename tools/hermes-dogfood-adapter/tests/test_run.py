from __future__ import annotations

import logging
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import run as adapter_run
from sync.checkpoint import CheckpointRecord, load_checkpoint
from sync.purr_writer import PurrWriter
from test_purr_writer import FakeBackend


class RunConfigTests(unittest.TestCase):
    def test_load_config_resolves_relative_paths_and_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.yaml"
            (root / "data").mkdir(parents=True)
            config_path.write_text(
                "\n".join(
                    [
                        'owner_id: "00000000-0000-0000-0000-000000000001"',
                        'purr_id: "00000000-0000-0000-0000-0000000000a1"',
                        'hermes_db_path: data/hermes.db',
                        'checkpoint_path: state/checkpoint.json',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            config = adapter_run.load_config(config_path)

            self.assertEqual(config.poll_interval, 30.0)
            self.assertEqual(config.hermes_db_path, (root / "data" / "hermes.db").resolve())
            self.assertEqual(config.checkpoint_path, (root / "state" / "checkpoint.json").resolve())
            self.assertEqual(config.log_dir, (root / "logs" / "dogfood").resolve())
            self.assertEqual(config.supabase_required_env, ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"))

    def test_shadow_adapter_enabled_understands_kill_switch_values(self) -> None:
        original = os.environ.get(adapter_run.KILL_SWITCH_ENV)
        try:
            os.environ[adapter_run.KILL_SWITCH_ENV] = "0"
            self.assertFalse(adapter_run.shadow_adapter_enabled())
            os.environ[adapter_run.KILL_SWITCH_ENV] = "false"
            self.assertFalse(adapter_run.shadow_adapter_enabled())
            os.environ[adapter_run.KILL_SWITCH_ENV] = "1"
            self.assertTrue(adapter_run.shadow_adapter_enabled())
            del os.environ[adapter_run.KILL_SWITCH_ENV]
            self.assertTrue(adapter_run.shadow_adapter_enabled())
        finally:
            if original is None:
                os.environ.pop(adapter_run.KILL_SWITCH_ENV, None)
            else:
                os.environ[adapter_run.KILL_SWITCH_ENV] = original


class ShadowAdapterCycleTests(unittest.TestCase):
    def test_cycle_defers_child_until_parent_exists_and_preserves_checkpoint_barrier(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "hermes.db"
            checkpoint_path = root / "state" / "checkpoint.json"
            self._create_sqlite_fixture(db_path)
            self._insert_session(
                db_path,
                session_id="sess-child",
                source="telegram",
                parent_session_id="sess-parent",
                started_at=10.0,
                ended_at=None,
                end_reason=None,
                title="child",
            )
            self._insert_session(
                db_path,
                session_id="sess-root",
                source="telegram",
                parent_session_id=None,
                started_at=20.0,
                ended_at=None,
                end_reason=None,
                title="root",
            )
            self._insert_message(db_path, message_id=1, session_id="sess-child", role="user", content="child", timestamp=100.0)
            self._insert_message(db_path, message_id=2, session_id="sess-root", role="assistant", content="root", timestamp=200.0)

            backend = FakeBackend()
            writer = PurrWriter(backend, batch_size=50)
            config = adapter_run.ShadowAdapterConfig(
                owner_id="00000000-0000-0000-0000-000000000001",
                purr_id="00000000-0000-0000-0000-0000000000a1",
                hermes_db_path=db_path,
                checkpoint_path=checkpoint_path,
                log_dir=root / "logs" / "dogfood",
            )
            logger = logging.getLogger("test_shadow_adapter_cycle")
            logger.handlers.clear()
            logger.addHandler(logging.NullHandler())
            adapter = adapter_run.ShadowAdapter(config, writer=writer, logger=logger)

            first_stats = adapter.run_once()

            self.assertEqual(first_stats.deferred_sessions, 1)
            self.assertEqual(first_stats.deferred_messages, 1)
            self.assertEqual(first_stats.messages_written, 1)
            self.assertIsNone(load_checkpoint(checkpoint_path))
            self.assertEqual(len(backend.table_rows.get("message_events", {})), 1)
            self.assertEqual(
                next(iter(backend.table_rows["message_events"].values()))["source_message_id"],
                "2",
            )

            self._insert_session(
                db_path,
                session_id="sess-parent",
                source="telegram",
                parent_session_id=None,
                started_at=5.0,
                ended_at=15.0,
                end_reason="compression",
                title="parent",
            )

            second_stats = adapter.run_once()
            checkpoint = load_checkpoint(checkpoint_path)

            self.assertEqual(second_stats.deferred_sessions, 0)
            self.assertEqual(second_stats.messages_written, 2)
            self.assertEqual(len(backend.table_rows.get("episodes", {})), 2)
            self.assertEqual(len(backend.table_rows.get("session_windows", {})), 3)
            self.assertEqual(len(backend.table_rows.get("message_events", {})), 2)
            self.assertEqual(
                checkpoint,
                CheckpointRecord(timestamp=200.0, message_id="2", session_id="sess-root"),
            )

    def test_dry_run_skips_checkpoint_updates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "hermes.db"
            checkpoint_path = root / "state" / "checkpoint.json"
            self._create_sqlite_fixture(db_path)
            self._insert_session(
                db_path,
                session_id="sess-root",
                source="telegram",
                parent_session_id=None,
                started_at=20.0,
                ended_at=None,
                end_reason=None,
                title="root",
            )
            self._insert_message(db_path, message_id=2, session_id="sess-root", role="assistant", content="root", timestamp=200.0)

            config = adapter_run.ShadowAdapterConfig(
                owner_id="00000000-0000-0000-0000-000000000001",
                purr_id="00000000-0000-0000-0000-0000000000a1",
                hermes_db_path=db_path,
                checkpoint_path=checkpoint_path,
                log_dir=root / "logs" / "dogfood",
            )
            logger = logging.getLogger("test_shadow_adapter_dry_run")
            logger.handlers.clear()
            logger.addHandler(logging.NullHandler())
            adapter = adapter_run.ShadowAdapter(config, writer=None, dry_run=True, logger=logger)

            stats = adapter.run_once()

            self.assertTrue(stats.dry_run)
            self.assertEqual(stats.messages_written, 1)
            self.assertIsNone(load_checkpoint(checkpoint_path))

    def _create_sqlite_fixture(self, db_path: Path) -> None:
        connection = sqlite3.connect(db_path)
        try:
            connection.execute(
                """
                CREATE TABLE sessions (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    user_id TEXT,
                    model TEXT,
                    model_config TEXT,
                    system_prompt TEXT,
                    parent_session_id TEXT,
                    started_at REAL NOT NULL,
                    ended_at REAL,
                    end_reason TEXT,
                    message_count INTEGER NOT NULL DEFAULT 0,
                    tool_call_count INTEGER NOT NULL DEFAULT 0,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    title TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    tool_call_id TEXT,
                    tool_calls TEXT,
                    tool_name TEXT,
                    timestamp REAL NOT NULL,
                    token_count INTEGER,
                    finish_reason TEXT
                )
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_session(
        self,
        db_path: Path,
        *,
        session_id: str,
        source: str,
        parent_session_id: str | None,
        started_at: float,
        ended_at: float | None,
        end_reason: str | None,
        title: str | None,
    ) -> None:
        connection = sqlite3.connect(db_path)
        try:
            connection.execute(
                """
                INSERT INTO sessions (
                    id,
                    source,
                    user_id,
                    model,
                    model_config,
                    system_prompt,
                    parent_session_id,
                    started_at,
                    ended_at,
                    end_reason,
                    message_count,
                    tool_call_count,
                    input_tokens,
                    output_tokens,
                    title
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    source,
                    "7469367760",
                    "test-model",
                    None,
                    None,
                    parent_session_id,
                    started_at,
                    ended_at,
                    end_reason,
                    1,
                    0,
                    10,
                    20,
                    title,
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_message(
        self,
        db_path: Path,
        *,
        message_id: int,
        session_id: str,
        role: str,
        content: str,
        timestamp: float,
    ) -> None:
        connection = sqlite3.connect(db_path)
        try:
            connection.execute(
                """
                INSERT INTO messages (
                    id,
                    session_id,
                    role,
                    content,
                    tool_call_id,
                    tool_calls,
                    tool_name,
                    timestamp,
                    token_count,
                    finish_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    session_id,
                    role,
                    content,
                    None,
                    None,
                    None,
                    timestamp,
                    5,
                    "stop",
                ),
            )
            connection.commit()
        finally:
            connection.close()
