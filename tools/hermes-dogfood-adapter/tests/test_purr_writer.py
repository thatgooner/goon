from __future__ import annotations

import unittest
from uuid import uuid4

from sync.purr_writer import (
    MemoryWriteBundle,
    PurrWriter,
    PurrWriterError,
    PurrWriterValidationError,
)


class FakeBackend:
    def __init__(self) -> None:
        self.upsert_calls: list[tuple[str, list[dict[str, object]], tuple[str, ...]]] = []
        self.table_rows: dict[str, dict[tuple[object, ...], dict[str, object]]] = {}
        self.memory_items: dict[tuple[str, str, str, str, str | None], dict[str, object]] = {}
        self.memory_events: dict[tuple[str, str, str], dict[str, object]] = {}
        self.memory_evidence_refs: dict[tuple[str, str, int, int], dict[str, object]] = {}
        self.rpc_calls: list[dict[str, object]] = []
        self.fail_on_rpc_call_number: int | None = None

    def upsert_rows(self, *, table: str, rows, on_conflict, resolution) -> None:
        rows = [dict(row) for row in rows]
        self.upsert_calls.append((table, rows, tuple(on_conflict), resolution))
        table_store = self.table_rows.setdefault(table, {})
        for row in rows:
            key = tuple(row.get(column) for column in on_conflict)
            if resolution == "merge-duplicates" and key in table_store:
                merged = dict(table_store[key])
                merged.update(row)
                table_store[key] = merged
                continue
            table_store.setdefault(key, row)

    def call_rpc(self, *, function_name: str, payload) -> dict[str, object]:
        self.rpc_calls.append({"function_name": function_name, "payload": dict(payload)})
        if self.fail_on_rpc_call_number is not None and len(self.rpc_calls) == self.fail_on_rpc_call_number:
            raise PurrWriterError("simulated rpc failure")

        if function_name == "sync_memory_events_phase0":
            inserted_memory_events = 0
            for row in [dict(item) for item in payload.get("memory_events", [])]:
                event_key = (
                    str(row["memory_id"]),
                    str(row["event_type"]),
                    str(row["intake_batch_key"]),
                )
                if event_key in self.memory_events:
                    continue
                self.memory_events[event_key] = row
                inserted_memory_events += 1
            return {"inserted_memory_events": inserted_memory_events}

        memory_item = dict(payload["memory_item"])
        events = [dict(row) for row in payload.get("memory_events", [])]
        evidence_refs = [dict(row) for row in payload.get("evidence_refs", [])]

        identity = (
            str(memory_item["owner_id"]),
            str(memory_item["purr_id"]),
            str(memory_item["dedupe_key"]),
            str(memory_item["durability_scope"]),
            None if memory_item.get("scope_ref") in (None, "") else str(memory_item["scope_ref"]),
        )
        inserted_memory_item = identity not in self.memory_items
        if inserted_memory_item:
            resolved_memory_id = str(memory_item.get("memory_id") or uuid4())
            stored_memory = dict(memory_item)
            stored_memory["memory_id"] = resolved_memory_id
            self.memory_items[identity] = stored_memory
        else:
            resolved_memory_id = str(self.memory_items[identity]["memory_id"])

        inserted_memory_events = 0
        for row in events:
            event_key = (
                resolved_memory_id,
                str(row["event_type"]),
                str(row["intake_batch_key"]),
            )
            if event_key in self.memory_events:
                continue
            stored_row = dict(row)
            stored_row["memory_id"] = resolved_memory_id
            self.memory_events[event_key] = stored_row
            inserted_memory_events += 1

        inserted_evidence_refs = 0
        for row in evidence_refs:
            evidence_key = (
                resolved_memory_id,
                str(row["message_id"]),
                int(row["span_start"]),
                int(row["span_end"]),
            )
            if evidence_key in self.memory_evidence_refs:
                continue
            stored_row = dict(row)
            stored_row["memory_id"] = resolved_memory_id
            self.memory_evidence_refs[evidence_key] = stored_row
            inserted_evidence_refs += 1

        return {
            "memory_id": resolved_memory_id,
            "inserted_memory_item": inserted_memory_item,
            "inserted_memory_events": inserted_memory_events,
            "inserted_evidence_refs": inserted_evidence_refs,
        }


class PurrWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = FakeBackend()
        self.writer = PurrWriter(self.backend, batch_size=2)
        self.owner_id = "00000000-0000-0000-0000-000000000001"
        self.purr_id = "00000000-0000-0000-0000-0000000000a1"
        self.episode_id = "10000000-0000-0000-0000-000000000001"
        self.window_id = "20000000-0000-0000-0000-000000000001"
        self.message_id = "30000000-0000-0000-0000-000000000001"

    def test_message_upserts_are_sorted_deduped_and_chunked(self) -> None:
        rows = [
            {
                "message_id": "b",
                "created_at": "2026-03-15T12:00:02Z",
                "owner_id": self.owner_id,
                "purr_id": self.purr_id,
            },
            {
                "message_id": "a",
                "created_at": "2026-03-15T12:00:01Z",
                "owner_id": self.owner_id,
                "purr_id": self.purr_id,
            },
            {
                "message_id": "b",
                "created_at": "2026-03-15T12:00:02Z",
                "owner_id": self.owner_id,
                "purr_id": self.purr_id,
            },
        ]

        result = self.writer.upsert_message_events(rows)

        self.assertEqual(result.table, "message_events")
        self.assertEqual(result.attempted, 3)
        self.assertEqual(result.submitted, 2)
        self.assertEqual(len(self.backend.upsert_calls), 1)
        table, submitted_rows, on_conflict, resolution = self.backend.upsert_calls[0]
        self.assertEqual(table, "message_events")
        self.assertEqual(on_conflict, ("message_id",))
        self.assertEqual(resolution, "ignore-duplicates")
        self.assertEqual([row["message_id"] for row in submitted_rows], ["a", "b"])
        self.assertEqual(len(self.backend.table_rows["message_events"]), 2)

    def test_episode_upserts_merge_latest_state(self) -> None:
        first = {
            "episode_id": self.episode_id,
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "kind": "daily_chat",
            "status": "open",
            "parent_episode_id": None,
            "started_at": "2026-03-15T12:00:00Z",
            "ended_at": None,
            "metadata_json": {"source_session_id": "sess-root"},
        }
        second = {
            "episode_id": self.episode_id,
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "kind": "daily_chat",
            "status": "closed",
            "parent_episode_id": None,
            "started_at": "2026-03-15T12:00:00Z",
            "ended_at": "2026-03-15T12:30:00Z",
            "metadata_json": {"source_session_id": "sess-root", "final": True},
        }

        self.writer.upsert_episodes([first])
        self.writer.upsert_episodes([second])

        stored = self.backend.table_rows["episodes"][(self.episode_id,)]
        self.assertEqual(stored["status"], "closed")
        self.assertEqual(stored["ended_at"], "2026-03-15T12:30:00Z")
        self.assertEqual(stored["metadata_json"], {"source_session_id": "sess-root", "final": True})

    def test_memory_bundle_replay_is_idempotent(self) -> None:
        bundle = self._make_memory_bundle()

        first = self.writer.write_memory_bundles([bundle])[0]
        second = self.writer.write_memory_bundles([bundle])[0]

        self.assertTrue(first.inserted_memory_item)
        self.assertEqual(first.inserted_memory_events, 1)
        self.assertEqual(first.inserted_evidence_refs, 1)
        self.assertFalse(second.inserted_memory_item)
        self.assertEqual(second.inserted_memory_events, 0)
        self.assertEqual(second.inserted_evidence_refs, 0)
        self.assertEqual(len(self.backend.memory_items), 1)
        self.assertEqual(len(self.backend.memory_events), 1)
        self.assertEqual(len(self.backend.memory_evidence_refs), 1)
        self.assertEqual(first.memory_id, second.memory_id)

    def test_memory_bundle_duplicates_within_batch_are_merged(self) -> None:
        base_bundle = self._make_memory_bundle()
        duplicate_bundle = MemoryWriteBundle(
            memory_item=dict(base_bundle.memory_item),
            memory_events=base_bundle.memory_events + base_bundle.memory_events,
            evidence_refs=base_bundle.evidence_refs + base_bundle.evidence_refs,
        )

        results = self.writer.write_memory_bundles([base_bundle, duplicate_bundle])

        self.assertEqual(len(results), 1)
        self.assertEqual(len(self.backend.rpc_calls), 1)
        payload = self.backend.rpc_calls[0]["payload"]
        self.assertEqual(len(payload["memory_events"]), 1)
        self.assertEqual(len(payload["evidence_refs"]), 1)

    def test_retry_after_mid_batch_failure_is_safe(self) -> None:
        first_bundle = self._make_memory_bundle(dedupe_key="drink.preference.coffee", intake_batch_key="batch-1")
        second_bundle = self._make_memory_bundle(
            dedupe_key="pet.name",
            memory_id="40000000-0000-0000-0000-000000000002",
            message_id="30000000-0000-0000-0000-000000000002",
            intake_batch_key="batch-2",
            excerpt_text="Mochi",
            excerpt_hash="hash-mochi",
        )

        self.backend.fail_on_rpc_call_number = 2
        with self.assertRaises(PurrWriterError):
            self.writer.write_memory_bundles([first_bundle, second_bundle])

        self.assertEqual(len(self.backend.memory_items), 1)
        self.assertEqual(len(self.backend.memory_events), 1)
        self.assertEqual(len(self.backend.memory_evidence_refs), 1)

        self.backend.fail_on_rpc_call_number = None
        results = self.writer.write_memory_bundles([first_bundle, second_bundle])

        self.assertEqual(len(results), 2)
        self.assertEqual(len(self.backend.memory_items), 2)
        self.assertEqual(len(self.backend.memory_events), 2)
        self.assertEqual(len(self.backend.memory_evidence_refs), 2)

    def test_memory_bundle_requires_evidence(self) -> None:
        bundle = MemoryWriteBundle(
            memory_item=self._make_memory_bundle().memory_item,
            memory_events=self._make_memory_bundle().memory_events,
            evidence_refs=(),
        )

        with self.assertRaises(PurrWriterValidationError):
            self.writer.write_memory_bundles([bundle])

    def test_memory_event_standalone_rpc_is_idempotent(self) -> None:
        row = {
            "memory_id": "40000000-0000-0000-0000-000000000001",
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "event_type": "created",
            "event_reason": "extractor",
            "actor_type": "extractor",
            "to_state": "candidate",
            "intake_batch_key": "batch-standalone",
            "delta_json": {"note": "phase0"},
            "created_at": "2026-03-15T12:00:01Z",
        }

        first = self.writer.upsert_memory_events([row, row])
        second = self.writer.upsert_memory_events([row])

        self.assertEqual(first.submitted, 1)
        self.assertEqual(first.inserted, 1)
        self.assertEqual(second.submitted, 1)
        self.assertEqual(second.inserted, 0)
        self.assertEqual(len(self.backend.memory_events), 1)

    def test_memory_events_require_intake_batch_key(self) -> None:
        bundle = self._make_memory_bundle(intake_batch_key="")

        with self.assertRaises(PurrWriterValidationError):
            self.writer.write_memory_bundles([bundle])

    def test_conflicting_duplicate_message_rows_raise(self) -> None:
        rows = [
            {
                "message_id": "same",
                "created_at": "2026-03-15T12:00:00Z",
                "owner_id": self.owner_id,
                "purr_id": self.purr_id,
                "content_text": "first",
            },
            {
                "message_id": "same",
                "created_at": "2026-03-15T12:00:00Z",
                "owner_id": self.owner_id,
                "purr_id": self.purr_id,
                "content_text": "second",
            },
        ]

        with self.assertRaises(PurrWriterValidationError):
            self.writer.upsert_message_events(rows)

    def test_memory_lane_must_be_private_1_1_in_phase_zero(self) -> None:
        bundle = self._make_memory_bundle(memory_lane="public_safe")

        with self.assertRaises(PurrWriterValidationError):
            self.writer.write_memory_bundles([bundle])

    def _make_memory_bundle(
        self,
        *,
        dedupe_key: str = "drink.preference.coffee",
        memory_id: str = "40000000-0000-0000-0000-000000000001",
        message_id: str | None = None,
        intake_batch_key: str = "batch-1",
        excerpt_text: str = "cold brew",
        excerpt_hash: str = "hash-cold-brew",
        memory_lane: str = "private_1_1",
    ) -> MemoryWriteBundle:
        effective_message_id = message_id or self.message_id
        memory_item = {
            "memory_id": memory_id,
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "memory_lane": memory_lane,
            "kind": "preference",
            "state": "candidate",
            "review_status": "none",
            "contradiction_status": "clean",
            "pack_policy": "shadow",
            "durability_scope": "profile",
            "is_exclusive": True,
            "subject_key": dedupe_key,
            "dedupe_key": dedupe_key,
            "scope_ref": self.owner_id,
            "episode_id": self.episode_id,
            "origin_window_id": self.window_id,
            "owner_surface": "world_chat",
            "confidence": 0.91,
            "salience": 0.78,
            "volatility": 0.20,
            "freshness_score": 0.90,
            "payload_json": {"value": excerpt_text},
            "created_at": "2026-03-15T12:00:00Z",
        }
        memory_event = {
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "event_type": "created",
            "event_reason": "extractor",
            "actor_type": "extractor",
            "to_state": "candidate",
            "intake_batch_key": intake_batch_key,
            "delta_json": {"note": "phase0"},
            "created_at": "2026-03-15T12:00:01Z",
        }
        evidence_ref = {
            "owner_id": self.owner_id,
            "purr_id": self.purr_id,
            "episode_id": self.episode_id,
            "window_id": self.window_id,
            "message_id": effective_message_id,
            "span_start": 0,
            "span_end": len(excerpt_text),
            "source_type": "chat",
            "excerpt_text": excerpt_text,
            "excerpt_hash": excerpt_hash,
            "evidence_weight": 1.0,
            "explicitness": "explicit",
            "speaker_role": "user",
            "captured_at": "2026-03-15T12:00:02Z",
        }
        return MemoryWriteBundle(
            memory_item=memory_item,
            memory_events=(memory_event,),
            evidence_refs=(evidence_ref,),
        )


if __name__ == "__main__":
    unittest.main()
