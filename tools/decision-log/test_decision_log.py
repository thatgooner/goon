#!/usr/bin/env python3
"""Tests for decision-log tool. Covers all testable_acceptance criteria from task board."""

import json
import os
import tempfile
import unittest

from decision_log import DecisionLog, _validate_entry, VALID_TYPES, REQUIRED_DETAIL_FIELDS


class TestValidation(unittest.TestCase):
    """Input validation tests."""

    def test_missing_type(self):
        errors = _validate_entry({"subject": "x", "detail": {}})
        self.assertTrue(any("type" in e for e in errors))

    def test_invalid_type(self):
        errors = _validate_entry({"type": "bogus", "subject": "x", "detail": {}})
        self.assertTrue(any("invalid type" in e for e in errors))

    def test_missing_subject(self):
        errors = _validate_entry({"type": "decision", "detail": {"options": [], "chose": "a", "reason": "b"}})
        self.assertTrue(any("subject" in e for e in errors))

    def test_empty_subject(self):
        errors = _validate_entry({"type": "decision", "subject": "  ", "detail": {"options": [], "chose": "a", "reason": "b"}})
        self.assertTrue(any("subject" in e for e in errors))

    def test_missing_detail(self):
        errors = _validate_entry({"type": "decision", "subject": "x"})
        self.assertTrue(any("detail" in e for e in errors))

    def test_detail_not_dict(self):
        errors = _validate_entry({"type": "decision", "subject": "x", "detail": "string"})
        self.assertTrue(any("detail" in e for e in errors))

    def test_decision_missing_detail_fields(self):
        errors = _validate_entry({"type": "decision", "subject": "x", "detail": {}})
        self.assertTrue(any("chose" in e or "options" in e or "reason" in e for e in errors))

    def test_silence_missing_detail_fields(self):
        errors = _validate_entry({"type": "silence", "subject": "x", "detail": {}})
        self.assertTrue(any("threshold" in e for e in errors))

    def test_handoff_missing_detail_fields(self):
        errors = _validate_entry({"type": "handoff", "subject": "x", "detail": {}})
        self.assertTrue(any("intent" in e or "from" in e or "to" in e for e in errors))

    def test_valid_decision(self):
        errors = _validate_entry({
            "type": "decision",
            "subject": "TheBotcave",
            "detail": {"options": ["upgrade", "keep", "kill"], "chose": "keep", "reason": "still no receipts"}
        })
        self.assertEqual(errors, [])

    def test_valid_silence(self):
        errors = _validate_entry({
            "type": "silence",
            "subject": "TheBotcave",
            "detail": {"threshold": "new repo or dashboard", "result": "3 posts, all commentary", "action_taken": False, "reason": "no receipts"}
        })
        self.assertEqual(errors, [])

    def test_valid_handoff(self):
        errors = _validate_entry({
            "type": "handoff",
            "subject": "suspicious skill X",
            "detail": {"intent": "audit skill X", "from": "gooner", "to": "code-worker"}
        })
        self.assertEqual(errors, [])

    def test_all_three_types_recognized(self):
        self.assertEqual(VALID_TYPES, {"decision", "silence", "handoff"})


class TestDecisionLogAdd(unittest.TestCase):
    """Tests for adding entries."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def _sample_decision(self):
        return {
            "type": "decision",
            "subject": "TheBotcave",
            "detail": {"options": ["upgrade", "keep", "kill"], "chose": "keep", "reason": "still no receipts"}
        }

    def _sample_silence(self):
        return {
            "type": "silence",
            "subject": "TheBotcave",
            "detail": {"threshold": "new repo or dashboard", "result": "3 posts, all commentary", "action_taken": False, "reason": "no receipts"}
        }

    def _sample_handoff(self):
        return {
            "type": "handoff",
            "subject": "suspicious skill X",
            "detail": {"intent": "audit skill X", "from": "gooner", "to": "code-worker"}
        }

    # --- Task board acceptance: must accept all 3 sample types ---

    def test_add_decision(self):
        entry = self.log.add(self._sample_decision())
        self.assertEqual(entry["type"], "decision")
        self.assertEqual(entry["subject"], "TheBotcave")
        self.assertEqual(entry["detail"]["chose"], "keep")
        self.assertIsNone(entry["resolution"])

    def test_add_silence(self):
        entry = self.log.add(self._sample_silence())
        self.assertEqual(entry["type"], "silence")
        self.assertEqual(entry["detail"]["action_taken"], False)
        self.assertIsNone(entry["resolution"])

    def test_add_handoff(self):
        entry = self.log.add(self._sample_handoff())
        self.assertEqual(entry["type"], "handoff")
        self.assertEqual(entry["detail"]["from"], "gooner")
        self.assertEqual(entry["detail"]["to"], "code-worker")
        self.assertIsNone(entry["resolution"])

    # --- Task board acceptance: id must be unique per entry ---

    def test_unique_ids(self):
        ids = set()
        for _ in range(100):
            entry = self.log.add(self._sample_decision())
            ids.add(entry["id"])
        self.assertEqual(len(ids), 100)

    def test_id_format(self):
        entry = self.log.add(self._sample_decision())
        self.assertIsInstance(entry["id"], str)
        self.assertEqual(len(entry["id"]), 12)

    # --- Output format fields ---

    def test_output_has_all_fields(self):
        entry = self.log.add(self._sample_decision())
        required_keys = {"id", "type", "timestamp", "subject", "detail", "resolution"}
        self.assertEqual(set(entry.keys()), required_keys)

    def test_timestamp_format(self):
        entry = self.log.add(self._sample_decision())
        ts = entry["timestamp"]
        self.assertTrue(ts.endswith("Z"))
        self.assertRegex(ts, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

    # --- Validation rejects bad input ---

    def test_add_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            self.log.add({"type": "bogus", "subject": "x", "detail": {}})

    def test_add_rejects_missing_subject(self):
        with self.assertRaises(ValueError):
            self.log.add({"type": "decision", "detail": {"options": [], "chose": "a", "reason": "b"}})


class TestRoundTrip(unittest.TestCase):
    """Task board acceptance: round-trip serialize/deserialize must preserve all fields."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def test_roundtrip_decision(self):
        original = self.log.add({
            "type": "decision",
            "subject": "TheBotcave",
            "detail": {"options": ["upgrade", "keep", "kill"], "chose": "keep", "reason": "still no receipts"}
        })
        entries = self.log.read_all()
        self.assertEqual(len(entries), 1)
        restored = entries[0]
        self.assertEqual(original, restored)

    def test_roundtrip_silence(self):
        original = self.log.add({
            "type": "silence",
            "subject": "TheBotcave",
            "detail": {"threshold": "new repo or dashboard", "result": "3 posts, all commentary", "action_taken": False, "reason": "no receipts"}
        })
        restored = self.log.read_all()[0]
        self.assertEqual(original, restored)

    def test_roundtrip_handoff(self):
        original = self.log.add({
            "type": "handoff",
            "subject": "suspicious skill X",
            "detail": {"intent": "audit skill X", "from": "gooner", "to": "code-worker"}
        })
        restored = self.log.read_all()[0]
        self.assertEqual(original, restored)

    def test_roundtrip_preserves_nested_types(self):
        """Booleans, lists, numbers in detail must survive serialization."""
        original = self.log.add({
            "type": "silence",
            "subject": "test",
            "detail": {
                "threshold": "x",
                "result": "y",
                "action_taken": False,
                "reason": "z",
                "extra_list": [1, 2, 3],
                "extra_float": 0.95,
                "extra_null": None,
            }
        })
        restored = self.log.read_all()[0]
        self.assertEqual(restored["detail"]["action_taken"], False)
        self.assertIsInstance(restored["detail"]["action_taken"], bool)
        self.assertEqual(restored["detail"]["extra_list"], [1, 2, 3])
        self.assertEqual(restored["detail"]["extra_float"], 0.95)
        self.assertIsNone(restored["detail"]["extra_null"])

    def test_roundtrip_unicode(self):
        """Unicode in subject/detail must survive."""
        original = self.log.add({
            "type": "decision",
            "subject": "Türkçe karakter testi — 🔥",
            "detail": {"options": ["evet", "hayır"], "chose": "evet", "reason": "çünkü öyle"}
        })
        restored = self.log.read_all()[0]
        self.assertEqual(original, restored)
        self.assertIn("Türkçe", restored["subject"])
        self.assertIn("🔥", restored["subject"])


class TestJSONLAppend(unittest.TestCase):
    """Task board acceptance: entries must be appendable to a JSONL file without corruption."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def test_multiple_appends(self):
        for i in range(10):
            self.log.add({
                "type": "decision",
                "subject": f"item-{i}",
                "detail": {"options": ["a", "b"], "chose": "a", "reason": f"reason-{i}"}
            })
        entries = self.log.read_all()
        self.assertEqual(len(entries), 10)
        for i, e in enumerate(entries):
            self.assertEqual(e["subject"], f"item-{i}")

    def test_mixed_type_appends(self):
        self.log.add({"type": "decision", "subject": "A", "detail": {"options": [], "chose": "x", "reason": "y"}})
        self.log.add({"type": "silence", "subject": "B", "detail": {"threshold": "t", "result": "r", "action_taken": True, "reason": "z"}})
        self.log.add({"type": "handoff", "subject": "C", "detail": {"intent": "i", "from": "g", "to": "c"}})
        entries = self.log.read_all()
        self.assertEqual(len(entries), 3)
        self.assertEqual([e["type"] for e in entries], ["decision", "silence", "handoff"])

    def test_each_line_is_valid_json(self):
        for i in range(5):
            self.log.add({"type": "decision", "subject": f"s{i}", "detail": {"options": [], "chose": "a", "reason": "b"}})
        with open(self.path, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertEqual(len(lines), 5)
        for line in lines:
            obj = json.loads(line)
            self.assertIn("id", obj)
            self.assertIn("type", obj)

    def test_no_trailing_corruption(self):
        self.log.add({"type": "decision", "subject": "x", "detail": {"options": [], "chose": "a", "reason": "b"}})
        with open(self.path, "r") as f:
            content = f.read()
        self.assertTrue(content.endswith("\n"))
        lines = content.split("\n")
        non_empty = [l for l in lines if l.strip()]
        self.assertEqual(len(non_empty), 1)

    def test_empty_file_read(self):
        entries = self.log.read_all()
        self.assertEqual(entries, [])

    def test_file_created_on_first_add(self):
        self.assertFalse(os.path.exists(self.path))
        self.log.add({"type": "decision", "subject": "x", "detail": {"options": [], "chose": "a", "reason": "b"}})
        self.assertTrue(os.path.exists(self.path))


class TestQuery(unittest.TestCase):
    """Query and filter tests."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)
        self.log.add({"type": "decision", "subject": "Alpha", "detail": {"options": [], "chose": "a", "reason": "b"}})
        self.log.add({"type": "silence", "subject": "Beta", "detail": {"threshold": "t", "result": "r", "action_taken": False, "reason": "z"}})
        self.log.add({"type": "handoff", "subject": "Alpha", "detail": {"intent": "i", "from": "g", "to": "c"}})

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def test_query_by_type(self):
        results = self.log.query(type="decision")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["subject"], "Alpha")

    def test_query_by_subject(self):
        results = self.log.query(subject="Alpha")
        self.assertEqual(len(results), 2)

    def test_query_by_type_and_subject(self):
        results = self.log.query(type="handoff", subject="Alpha")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "handoff")

    def test_query_no_match(self):
        results = self.log.query(subject="Nonexistent")
        self.assertEqual(results, [])

    def test_query_all(self):
        results = self.log.query()
        self.assertEqual(len(results), 3)


class TestResolve(unittest.TestCase):
    """Resolution tests."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def test_resolve_entry(self):
        entry = self.log.add({"type": "decision", "subject": "X", "detail": {"options": [], "chose": "a", "reason": "b"}})
        resolved = self.log.resolve(entry["id"], "confirmed after 7 days")
        self.assertEqual(resolved["resolution"], "confirmed after 7 days")
        reloaded = self.log.read_all()
        self.assertEqual(reloaded[0]["resolution"], "confirmed after 7 days")

    def test_resolve_preserves_other_entries(self):
        e1 = self.log.add({"type": "decision", "subject": "A", "detail": {"options": [], "chose": "a", "reason": "b"}})
        e2 = self.log.add({"type": "silence", "subject": "B", "detail": {"threshold": "t", "result": "r", "action_taken": False, "reason": "z"}})
        self.log.resolve(e1["id"], "done")
        entries = self.log.read_all()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["resolution"], "done")
        self.assertIsNone(entries[1]["resolution"])

    def test_resolve_unknown_id(self):
        with self.assertRaises(KeyError):
            self.log.resolve("nonexistent", "x")

    def test_resolve_roundtrip(self):
        entry = self.log.add({"type": "handoff", "subject": "Y", "detail": {"intent": "i", "from": "g", "to": "c"}})
        self.log.resolve(entry["id"], "completed by code-worker")
        entries = self.log.read_all()
        self.assertEqual(entries[0]["resolution"], "completed by code-worker")
        all_keys = set(entries[0].keys())
        self.assertEqual(all_keys, {"id", "type", "timestamp", "subject", "detail", "resolution"})


class TestTaskBoardSamples(unittest.TestCase):
    """Exact task board sample inputs — must all work correctly."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test.jsonl")
        self.log = DecisionLog(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.rmdir(self.tmpdir)

    def test_sample_decision(self):
        """decision: 'should TheBotcave be upgraded from watch to trusted?'"""
        entry = self.log.add({
            "type": "decision",
            "subject": "TheBotcave",
            "detail": {
                "options": ["upgrade", "keep", "kill"],
                "chose": "keep",
                "reason": "still no receipts"
            }
        })
        self.assertEqual(entry["type"], "decision")
        self.assertEqual(entry["subject"], "TheBotcave")
        self.assertEqual(entry["detail"]["options"], ["upgrade", "keep", "kill"])
        self.assertEqual(entry["detail"]["chose"], "keep")
        self.assertEqual(entry["detail"]["reason"], "still no receipts")
        self.assertIsNotNone(entry["id"])
        self.assertIsNotNone(entry["timestamp"])
        self.assertIsNone(entry["resolution"])

    def test_sample_silence(self):
        """silence: checked TheBotcave timeline, threshold='new repo or dashboard'"""
        entry = self.log.add({
            "type": "silence",
            "subject": "TheBotcave",
            "detail": {
                "threshold": "new repo or dashboard",
                "result": "3 posts, all commentary",
                "action_taken": False,
                "reason": "no receipts"
            }
        })
        self.assertEqual(entry["type"], "silence")
        self.assertEqual(entry["detail"]["threshold"], "new repo or dashboard")
        self.assertEqual(entry["detail"]["action_taken"], False)

    def test_sample_handoff(self):
        """handoff: gooner found suspicious skill, needs code-worker to scan it"""
        entry = self.log.add({
            "type": "handoff",
            "subject": "suspicious skill X",
            "detail": {
                "intent": "audit skill X",
                "from": "gooner",
                "to": "code-worker"
            }
        })
        self.assertEqual(entry["type"], "handoff")
        self.assertEqual(entry["detail"]["intent"], "audit skill X")
        self.assertEqual(entry["detail"]["from"], "gooner")
        self.assertEqual(entry["detail"]["to"], "code-worker")

    def test_all_three_samples_coexist_in_file(self):
        """All 3 sample types appended to same file, round-trip intact."""
        e1 = self.log.add({
            "type": "decision",
            "subject": "TheBotcave",
            "detail": {"options": ["upgrade", "keep", "kill"], "chose": "keep", "reason": "still no receipts"}
        })
        e2 = self.log.add({
            "type": "silence",
            "subject": "TheBotcave",
            "detail": {"threshold": "new repo or dashboard", "result": "3 posts, all commentary", "action_taken": False, "reason": "no receipts"}
        })
        e3 = self.log.add({
            "type": "handoff",
            "subject": "suspicious skill X",
            "detail": {"intent": "audit skill X", "from": "gooner", "to": "code-worker"}
        })

        entries = self.log.read_all()
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0], e1)
        self.assertEqual(entries[1], e2)
        self.assertEqual(entries[2], e3)

        ids = {e["id"] for e in entries}
        self.assertEqual(len(ids), 3)


if __name__ == "__main__":
    unittest.main()
