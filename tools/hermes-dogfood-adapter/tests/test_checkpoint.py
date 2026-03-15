from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sync.checkpoint import (
    CheckpointError,
    CheckpointFormatError,
    CheckpointRecord,
    LocalCheckpointStore,
    advance_checkpoint,
    checkpoint_for_batch,
    compare_checkpoints,
    is_message_after_checkpoint,
    load_checkpoint,
    save_checkpoint,
)
from sync.hermes_reader import HermesMessage


class CheckpointTests(unittest.TestCase):
    def test_load_missing_checkpoint_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checkpoint.json"
            self.assertIsNone(load_checkpoint(path))

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state" / "checkpoint.json"
            checkpoint = CheckpointRecord(
                timestamp=1700000002.5,
                message_id=42,
                session_id="sess-root",
            )

            saved = save_checkpoint(path, checkpoint)
            loaded = load_checkpoint(path)

            self.assertEqual(saved.message_id, "42")
            self.assertEqual(loaded, saved)
            self.assertEqual(loaded.session_id, "sess-root")

    def test_load_rejects_malformed_checkpoint_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checkpoint.json"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaises(CheckpointFormatError) as error:
                load_checkpoint(path)

            self.assertIn("Invalid checkpoint JSON", str(error.exception))

    def test_load_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checkpoint.json"
            path.write_text('{"schema_version":1,"last_processed_timestamp":1700000000.0}', encoding="utf-8")

            with self.assertRaises(CheckpointFormatError) as error:
                load_checkpoint(path)

            self.assertIn("last_processed_message_id", str(error.exception))

    def test_compare_and_filter_use_timestamp_then_message_id(self) -> None:
        checkpoint = CheckpointRecord(timestamp=1700000001.0, message_id="2", session_id="sess-root")
        older_same_timestamp = self._make_message(message_id=1, timestamp=1700000001.0)
        same_position = self._make_message(message_id=2, timestamp=1700000001.0)
        newer_same_timestamp = self._make_message(message_id=3, timestamp=1700000001.0)
        newer_timestamp = self._make_message(message_id=1, timestamp=1700000002.0)

        self.assertFalse(is_message_after_checkpoint(older_same_timestamp, checkpoint))
        self.assertFalse(is_message_after_checkpoint(same_position, checkpoint))
        self.assertTrue(is_message_after_checkpoint(newer_same_timestamp, checkpoint))
        self.assertTrue(is_message_after_checkpoint(newer_timestamp, checkpoint))
        self.assertLess(
            compare_checkpoints(
                CheckpointRecord(timestamp=1700000001.0, message_id="2"),
                CheckpointRecord(timestamp=1700000001.0, message_id="10"),
            ),
            0,
        )

    def test_checkpoint_for_batch_returns_latest_message_even_if_unsorted(self) -> None:
        messages = [
            self._make_message(message_id=5, timestamp=1700000001.0, session_id="sess-a"),
            self._make_message(message_id=3, timestamp=1700000003.0, session_id="sess-b"),
            self._make_message(message_id=4, timestamp=1700000003.0, session_id="sess-c"),
            self._make_message(message_id=2, timestamp=1700000002.0, session_id="sess-a"),
        ]

        checkpoint = checkpoint_for_batch(messages)

        self.assertEqual(checkpoint, CheckpointRecord(timestamp=1700000003.0, message_id="4", session_id="sess-c"))

    def test_store_advance_only_moves_forward(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalCheckpointStore(Path(temp_dir) / "checkpoint.json")
            first = CheckpointRecord(timestamp=1700000001.0, message_id="10", session_id="sess-a")
            older = CheckpointRecord(timestamp=1700000000.0, message_id="999", session_id="sess-b")
            newer = CheckpointRecord(timestamp=1700000002.0, message_id="1", session_id="sess-c")

            store.save(first)
            self.assertEqual(store.advance(older), first)
            self.assertEqual(store.load(), first)
            self.assertEqual(advance_checkpoint(first, older), first)

            self.assertEqual(store.advance(newer), newer)
            self.assertEqual(store.load(), newer)

    def test_atomic_save_preserves_existing_checkpoint_on_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checkpoint.json"
            original = CheckpointRecord(timestamp=1700000001.0, message_id="1", session_id="sess-a")
            updated = CheckpointRecord(timestamp=1700000002.0, message_id="2", session_id="sess-b")
            save_checkpoint(path, original)

            with mock.patch("sync.checkpoint.os.replace", side_effect=OSError("boom")):
                with self.assertRaises(CheckpointError):
                    save_checkpoint(path, updated)

            self.assertEqual(load_checkpoint(path), original)
            self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])

    @staticmethod
    def _make_message(
        *,
        message_id: int,
        timestamp: float,
        session_id: str = "sess-root",
    ) -> HermesMessage:
        return HermesMessage(
            id=message_id,
            session_id=session_id,
            role="user",
            content="hello",
            tool_call_id=None,
            tool_calls=None,
            tool_calls_raw=None,
            tool_name=None,
            timestamp=timestamp,
            token_count=1,
            finish_reason=None,
        )


if __name__ == "__main__":
    unittest.main()
