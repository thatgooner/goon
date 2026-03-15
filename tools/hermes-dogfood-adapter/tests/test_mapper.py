from __future__ import annotations

import unittest

from sync.hermes_reader import HermesMessage, HermesSession
from sync.mapper import MapperConfig, map_message_role, map_messages_for_session, map_session_bundle


class MapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = MapperConfig(
            owner_id="00000000-0000-0000-0000-000000000001",
            purr_id="00000000-0000-0000-0000-0000000000a1",
        )

    def test_root_session_bundle_is_deterministic(self) -> None:
        session = HermesSession(
            id="sess-root",
            source="telegram",
            user_id="7469367760",
            model="test-model",
            model_config=None,
            model_config_raw=None,
            system_prompt="prompt",
            parent_session_id=None,
            started_at=1700000000.0,
            ended_at=None,
            end_reason=None,
            message_count=2,
            tool_call_count=0,
            input_tokens=10,
            output_tokens=20,
            title="root",
        )
        messages = [
            HermesMessage(
                id=1,
                session_id="sess-root",
                role="user",
                content="hello",
                tool_call_id=None,
                tool_calls=None,
                tool_calls_raw=None,
                tool_name=None,
                timestamp=1700000001.0,
                token_count=5,
                finish_reason=None,
            ),
            HermesMessage(
                id=2,
                session_id="sess-root",
                role="assistant",
                content="yo",
                tool_call_id=None,
                tool_calls=None,
                tool_calls_raw=None,
                tool_name=None,
                timestamp=1700000002.0,
                token_count=6,
                finish_reason="stop",
            ),
        ]

        first = map_session_bundle(session, messages, config=self.config)
        second = map_session_bundle(session, messages, config=self.config)

        self.assertEqual(first.context.episode_id, second.context.episode_id)
        self.assertEqual(first.context.window_id, second.context.window_id)
        self.assertEqual(first.messages[0]["message_id"], second.messages[0]["message_id"])
        self.assertEqual(first.window["entry_surface"], "world_chat")
        self.assertEqual(first.messages[0]["role"], "user")
        self.assertEqual(first.messages[1]["role"], "purr")
        self.assertIsNotNone(first.episode)

    def test_child_session_reuses_episode_and_links_parent_window_without_new_episode_row(self) -> None:
        root_session = HermesSession(
            id="sess-root",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id=None,
            started_at=1700000000.0,
            ended_at=1700000100.0,
            end_reason="compression",
            message_count=1,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )
        root_bundle = map_session_bundle(root_session, [], config=self.config)

        child_session = HermesSession(
            id="sess-child",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id="sess-root",
            started_at=1700000200.0,
            ended_at=1700000300.0,
            end_reason="done",
            message_count=0,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )

        child_bundle = map_session_bundle(
            child_session,
            [],
            config=self.config,
            parent_context=root_bundle.context,
        )

        self.assertEqual(child_bundle.context.episode_id, root_bundle.context.episode_id)
        self.assertEqual(child_bundle.context.parent_window_id, root_bundle.context.window_id)
        self.assertEqual(child_bundle.context.episode_started_at, root_bundle.context.episode_started_at)
        self.assertIsNone(child_bundle.episode)
        self.assertEqual(child_bundle.window["episode_id"], root_bundle.context.episode_id)

    def test_unknown_role_raises(self) -> None:
        with self.assertRaises(ValueError):
            map_message_role("alien")

    def test_child_session_requires_matching_parent_context(self) -> None:
        child_session = HermesSession(
            id="sess-child",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id="sess-root",
            started_at=1700000200.0,
            ended_at=None,
            end_reason=None,
            message_count=0,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )

        with self.assertRaises(ValueError):
            map_session_bundle(child_session, [], config=self.config)

    def test_messages_are_sorted_stably_before_mapping(self) -> None:
        root_session = HermesSession(
            id="sess-root",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id=None,
            started_at=1700000000.0,
            ended_at=None,
            end_reason=None,
            message_count=2,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )
        bundle = map_session_bundle(root_session, [], config=self.config)

        messages = [
            HermesMessage(
                id=2,
                session_id="sess-root",
                role="assistant",
                content="  later  ",
                tool_call_id=None,
                tool_calls=None,
                tool_calls_raw=None,
                tool_name="memory",
                timestamp=1700000002.0,
                token_count=2,
                finish_reason=None,
            ),
            HermesMessage(
                id=1,
                session_id="sess-root",
                role="system",
                content="earlier",
                tool_call_id=None,
                tool_calls=None,
                tool_calls_raw=None,
                tool_name=None,
                timestamp=1700000001.0,
                token_count=1,
                finish_reason=None,
            ),
        ]

        mapped = map_messages_for_session(messages, context=bundle.context, config=self.config)
        self.assertEqual([row["source_message_id"] for row in mapped], ["1", "2"])
        self.assertEqual(mapped[0]["role"], "system")
        self.assertEqual(mapped[1]["tool_visibility"], "hidden")
        self.assertEqual(mapped[1]["content_text"], "  later  ")

    def test_child_session_rejects_parent_context_identity_mismatch(self) -> None:
        root_session = HermesSession(
            id="sess-root",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id=None,
            started_at=1700000000.0,
            ended_at=None,
            end_reason=None,
            message_count=0,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )
        root_bundle = map_session_bundle(root_session, [], config=self.config)

        mismatched_config = MapperConfig(
            owner_id="00000000-0000-0000-0000-000000000002",
            purr_id="00000000-0000-0000-0000-0000000000b2",
        )
        child_session = HermesSession(
            id="sess-child",
            source="telegram",
            user_id="7469367760",
            model=None,
            model_config=None,
            model_config_raw=None,
            system_prompt=None,
            parent_session_id="sess-root",
            started_at=1700000200.0,
            ended_at=None,
            end_reason=None,
            message_count=0,
            tool_call_count=0,
            input_tokens=0,
            output_tokens=0,
            title=None,
        )

        with self.assertRaises(ValueError):
            map_session_bundle(
                child_session,
                [],
                config=mismatched_config,
                parent_context=root_bundle.context,
            )


if __name__ == "__main__":
    unittest.main()
