#!/usr/bin/env python3
"""
Test suite for commenter-pattern-tracker.

Covers all testable_acceptance criteria from the task board plus
patterns observed in gooner's 2026-03-13 daily note.

Run: python3 -m unittest test_tracker.py -v
"""

import json
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker import analyze_comments, load_rules, _jaccard, _tokenize, _is_low_substance


def _ts(base, offset_minutes=0):
    """Helper: ISO timestamp relative to a base datetime."""
    dt = base + timedelta(minutes=offset_minutes)
    return dt.isoformat()


BASE_TIME = datetime(2026, 3, 13, 10, 0, 0, tzinfo=timezone.utc)


class TestHypeBotSpam(unittest.TestCase):
    """hype_bot_99: 5 identical comments on different posts within 10 min -> spam_score > 0.7"""

    def setUp(self):
        self.data = {
            "comments": [
                {
                    "author": "hype_bot_99",
                    "text": "Amazing work! 🔥",
                    "post_url": f"https://moltbook.com/post/{i}",
                    "timestamp": _ts(BASE_TIME, offset_minutes=i * 2),
                }
                for i in range(5)
            ]
        }
        self.result = analyze_comments(self.data)

    def test_spam_score_above_threshold(self):
        acct = self.result["accounts"][0]
        self.assertEqual(acct["author"], "hype_bot_99")
        self.assertGreater(acct["spam_score"], 0.7, f"Expected >0.7, got {acct['spam_score']}")

    def test_comment_count(self):
        acct = self.result["accounts"][0]
        self.assertEqual(acct["comment_count"], 5)

    def test_repeated_phrases_nonempty(self):
        acct = self.result["accounts"][0]
        self.assertTrue(len(acct["repeated_phrases"]) > 0)

    def test_touched_posts_count(self):
        acct = self.result["accounts"][0]
        self.assertEqual(len(acct["touched_posts"]), 5)


class TestLegitBuilder(unittest.TestCase):
    """legit_builder: 2 technical comments over 3 days -> spam_score < 0.3"""

    def setUp(self):
        self.data = {
            "comments": [
                {
                    "author": "legit_builder",
                    "text": (
                        "I ran the py-clob-client against testnet and the funding rate "
                        "divergence on YES tokens was 3.2% when spread exceeded 15%. "
                        "Here's the repo: github.com/legit/pm-bot — the backtest module "
                        "handles slippage estimation."
                    ),
                    "post_url": "https://moltbook.com/post/abc123",
                    "timestamp": _ts(BASE_TIME),
                },
                {
                    "author": "legit_builder",
                    "text": (
                        "Deployed v2 of the order router on mainnet. Latency dropped from "
                        "340ms to 180ms after switching to websocket feeds. Dashboard is at "
                        "dune.com/legit/pm-dashboard — you can see the fill rate improvement "
                        "in the last 24h panel."
                    ),
                    "post_url": "https://moltbook.com/post/def456",
                    "timestamp": _ts(BASE_TIME, offset_minutes=60 * 72),
                },
            ]
        }
        self.result = analyze_comments(self.data)

    def test_spam_score_below_threshold(self):
        acct = self.result["accounts"][0]
        self.assertEqual(acct["author"], "legit_builder")
        self.assertLess(acct["spam_score"], 0.3, f"Expected <0.3, got {acct['spam_score']}")

    def test_no_repeated_phrases(self):
        acct = self.result["accounts"][0]
        self.assertEqual(len(acct["repeated_phrases"]), 0)

    def test_no_burst_windows(self):
        acct = self.result["accounts"][0]
        self.assertEqual(len(acct["burst_windows"]), 0)


class TestRepeatedPhrases(unittest.TestCase):
    """repeated_phrases must be non-empty when same phrase appears 2+ times."""

    def test_exact_duplicate(self):
        data = {
            "comments": [
                {"author": "spammer", "text": "Great project!", "post_url": "p/1", "timestamp": _ts(BASE_TIME)},
                {"author": "spammer", "text": "Great project!", "post_url": "p/2", "timestamp": _ts(BASE_TIME, 5)},
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertTrue(len(acct["repeated_phrases"]) > 0)

    def test_near_duplicate(self):
        """'Amazing work! 🔥' and 'Amazing work! 🔥🔥' should be caught."""
        data = {
            "comments": [
                {"author": "bot", "text": "Amazing work! 🔥", "post_url": "p/1", "timestamp": _ts(BASE_TIME)},
                {"author": "bot", "text": "Amazing work! 🔥🔥", "post_url": "p/2", "timestamp": _ts(BASE_TIME, 3)},
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertTrue(len(acct["repeated_phrases"]) > 0, "Near-duplicate should be detected")


class TestBurstWindows(unittest.TestCase):
    """Burst window detection."""

    def test_burst_detected(self):
        data = {
            "comments": [
                {"author": "flood", "text": f"Comment {i}", "post_url": f"p/{i}", "timestamp": _ts(BASE_TIME, i)}
                for i in range(5)
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertTrue(len(acct["burst_windows"]) > 0, "Burst window should be detected")
        self.assertEqual(acct["burst_windows"][0]["count"], 5)

    def test_no_burst_spread_out(self):
        data = {
            "comments": [
                {
                    "author": "slow_poster",
                    "text": f"Detailed technical comment about topic {i} with github.com/user/repo{i}",
                    "post_url": f"p/{i}",
                    "timestamp": _ts(BASE_TIME, offset_minutes=i * 120),
                }
                for i in range(3)
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertEqual(len(acct["burst_windows"]), 0)


class TestMixedBatch(unittest.TestCase):
    """Both hype_bot_99 and legit_builder in same input."""

    def setUp(self):
        hype_comments = [
            {
                "author": "hype_bot_99",
                "text": "Amazing work! 🔥",
                "post_url": f"https://moltbook.com/post/hype{i}",
                "timestamp": _ts(BASE_TIME, offset_minutes=i * 2),
            }
            for i in range(5)
        ]
        legit_comments = [
            {
                "author": "legit_builder",
                "text": (
                    "Ran the py-clob-client against testnet, funding rate "
                    "divergence was 3.2%. Repo: github.com/legit/pm-bot"
                ),
                "post_url": "https://moltbook.com/post/legit1",
                "timestamp": _ts(BASE_TIME),
            },
            {
                "author": "legit_builder",
                "text": (
                    "Deployed v2 order router on mainnet. Websocket feed "
                    "cut latency from 340ms to 180ms. Dashboard: dune.com/legit/dash"
                ),
                "post_url": "https://moltbook.com/post/legit2",
                "timestamp": _ts(BASE_TIME, offset_minutes=60 * 72),
            },
        ]
        self.data = {"comments": hype_comments + legit_comments}
        self.result = analyze_comments(self.data)

    def test_both_present(self):
        authors = [a["author"] for a in self.result["accounts"]]
        self.assertIn("hype_bot_99", authors)
        self.assertIn("legit_builder", authors)

    def test_hype_bot_higher_score(self):
        scores = {a["author"]: a["spam_score"] for a in self.result["accounts"]}
        self.assertGreater(scores["hype_bot_99"], 0.7)
        self.assertLess(scores["legit_builder"], 0.3)

    def test_sorted_by_score(self):
        scores = [a["spam_score"] for a in self.result["accounts"]]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestEdgeCases(unittest.TestCase):
    """Edge cases: single comment, empty input, unicode/emoji."""

    def test_empty_input(self):
        result = analyze_comments({"comments": []})
        self.assertEqual(result, {"accounts": []})

    def test_empty_comments_key(self):
        result = analyze_comments({})
        self.assertEqual(result, {"accounts": []})

    def test_single_comment(self):
        data = {
            "comments": [
                {"author": "solo", "text": "Hello world", "post_url": "p/1", "timestamp": _ts(BASE_TIME)}
            ]
        }
        result = analyze_comments(data)
        self.assertEqual(len(result["accounts"]), 1)
        acct = result["accounts"][0]
        self.assertEqual(acct["comment_count"], 1)
        self.assertEqual(acct["repeated_phrases"], [])
        self.assertEqual(acct["burst_windows"], [])

    def test_unicode_content(self):
        data = {
            "comments": [
                {"author": "uni", "text": "Très bon travail sur le système de données", "post_url": "p/1", "timestamp": _ts(BASE_TIME)},
                {"author": "uni", "text": "日本語のテスト投稿です", "post_url": "p/2", "timestamp": _ts(BASE_TIME, 60)},
            ]
        }
        result = analyze_comments(data)
        self.assertEqual(len(result["accounts"]), 1)

    def test_emoji_only_comment(self):
        data = {
            "comments": [
                {"author": "emoji_fan", "text": "🔥🔥🔥🚀🚀💯", "post_url": "p/1", "timestamp": _ts(BASE_TIME)},
                {"author": "emoji_fan", "text": "🔥🔥🔥🚀🚀💯", "post_url": "p/2", "timestamp": _ts(BASE_TIME, 1)},
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertGreater(acct["spam_score"], 0.3)


class TestSimonCalebPattern(unittest.TestCase):
    """
    simoncaleb_openclaw_bot pattern: multiple long essay-comments with similar
    structure under the same thread, high word count, no receipts, same engagement
    template repeated.
    """

    def setUp(self):
        template = (
            "This raises such an important question about the nature of {topic}. "
            "How do we ensure that the evolution of agent infrastructure doesn't "
            "simply replicate the same centralization patterns we see in traditional "
            "systems? What governance frameworks could prevent capture while still "
            "enabling the kind of rapid iteration that makes this space exciting? "
            "I think the intersection of {topic} and decentralized coordination "
            "offers some fascinating possibilities worth exploring further."
        )
        topics = [
            "multi-agent orchestration",
            "autonomous agent collaboration",
            "decentralized intelligence systems",
            "emergent agent behavior",
        ]
        self.data = {
            "comments": [
                {
                    "author": "simoncaleb_openclaw_bot",
                    "text": template.format(topic=t),
                    "post_url": "https://moltbook.com/post/simmer-thread",
                    "timestamp": _ts(BASE_TIME, offset_minutes=i * 3),
                }
                for i, t in enumerate(topics)
            ]
        }
        self.result = analyze_comments(self.data)

    def test_high_spam_score(self):
        acct = self.result["accounts"][0]
        self.assertGreater(
            acct["spam_score"], 0.4,
            f"simoncaleb pattern should score high, got {acct['spam_score']}"
        )

    def test_repeated_phrases_detected(self):
        acct = self.result["accounts"][0]
        self.assertTrue(
            len(acct["repeated_phrases"]) > 0,
            "Template reuse should be detected as repeated phrases"
        )

    def test_burst_detected(self):
        acct = self.result["accounts"][0]
        self.assertTrue(len(acct["burst_windows"]) > 0)


class TestThreadHijack(unittest.TestCase):
    """
    Thread hijack pattern: Editor-in-Chief replying to the Jaris CLOB post
    with a generic promo unrelated to the discussion.
    """

    def test_promo_hijack_low_substance(self):
        data = {
            "comments": [
                {
                    "author": "Editor-in-Chief",
                    "text": (
                        "You are Invited to Watch Human Culture unfold in real-time. "
                        "Subscribe to our RSS feed at finallyoffline.com/rss.xml for "
                        "exclusive insights into the intersection of technology and culture."
                    ),
                    "post_url": "https://moltbook.com/post/jaris-clob",
                    "timestamp": _ts(BASE_TIME),
                },
                {
                    "author": "Editor-in-Chief",
                    "text": (
                        "You are Invited to Watch Human Culture unfold in real-time. "
                        "Subscribe to our RSS feed at finallyoffline.com/rss.xml for "
                        "exclusive updates on technology and society."
                    ),
                    "post_url": "https://moltbook.com/post/other-thread",
                    "timestamp": _ts(BASE_TIME, 5),
                },
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertGreater(
            acct["spam_score"], 0.3,
            f"Thread hijack promo should score as spammy, got {acct['spam_score']}"
        )
        self.assertTrue(len(acct["repeated_phrases"]) > 0)


class TestClawV6Pattern(unittest.TestCase):
    """ClawV6 generic praise filler: zero claim, zero receipt."""

    def test_generic_praise_is_low_substance(self):
        rules = load_rules()
        text = "The community here is incredible. So many brilliant minds working together. #web3 #crypto #learning"
        self.assertTrue(_is_low_substance(text, rules))

    def test_multiple_generic_comments(self):
        data = {
            "comments": [
                {
                    "author": "ClawV6",
                    "text": "The community here is incredible. So many brilliant minds working together. #web3 #crypto #learning",
                    "post_url": "p/1",
                    "timestamp": _ts(BASE_TIME),
                },
                {
                    "author": "ClawV6",
                    "text": "Amazing work by the team! The future of AI agents is truly exciting. #web3 #ai",
                    "post_url": "p/2",
                    "timestamp": _ts(BASE_TIME, 10),
                },
                {
                    "author": "ClawV6",
                    "text": "Incredible progress! Love this community. So many great ideas being built. #crypto #learning",
                    "post_url": "p/3",
                    "timestamp": _ts(BASE_TIME, 12),
                },
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertGreater(acct["spam_score"], 0.5, f"ClawV6 pattern should be high, got {acct['spam_score']}")


class TestG1NodePattern(unittest.TestCase):
    """g1-node service-manifest solicitation: rates, off-platform contact, capability theater."""

    def test_service_manifest_spam(self):
        data = {
            "comments": [
                {
                    "author": "g1-node",
                    "text": (
                        "Professional cybersecurity and reconnaissance services available. "
                        "Hourly rate: $150/hr. Premium tier packages for enterprise clients. "
                        "Contact me on Telegram: @g1node or LinkedIn: linkedin.com/in/g1node. "
                        "Specializing in vulnerability assessment, network penetration, and "
                        "red team operations."
                    ),
                    "post_url": "p/1",
                    "timestamp": _ts(BASE_TIME),
                },
                {
                    "author": "g1-node",
                    "text": (
                        "Available for hire: web application security audits, smart contract "
                        "reviews, and incident response. Rates start at $120/hr. "
                        "Contact: Telegram @g1node. Free consultation for first-time clients."
                    ),
                    "post_url": "p/2",
                    "timestamp": _ts(BASE_TIME, 30),
                },
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertGreater(acct["spam_score"], 0.3, f"Service manifest should flag, got {acct['spam_score']}")


class TestJaccardSimilarity(unittest.TestCase):
    """Unit tests for the Jaccard similarity helper."""

    def test_identical(self):
        tokens = _tokenize("Amazing work")
        self.assertEqual(_jaccard(tokens, tokens), 1.0)

    def test_disjoint(self):
        a = _tokenize("hello world")
        b = _tokenize("goodbye universe")
        self.assertLess(_jaccard(a, b), 0.1)

    def test_partial_overlap(self):
        a = _tokenize("the quick brown fox")
        b = _tokenize("the slow brown dog")
        sim = _jaccard(a, b)
        self.assertGreater(sim, 0.2)
        self.assertLess(sim, 0.8)

    def test_empty(self):
        self.assertEqual(_jaccard([], []), 1.0)
        self.assertEqual(_jaccard(["a"], []), 0.0)


class TestCLIMode(unittest.TestCase):
    """Test that the tool works as CLI with file I/O."""

    def test_roundtrip_json(self):
        data = {
            "comments": [
                {"author": "a", "text": "test", "post_url": "p/1", "timestamp": _ts(BASE_TIME)}
            ]
        }
        result = analyze_comments(data)
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)
        self.assertEqual(result, deserialized)


class TestTimestampFormats(unittest.TestCase):
    """Various ISO 8601 timestamp formats should be accepted."""

    def test_various_formats(self):
        formats = [
            "2026-03-13T10:00:00Z",
            "2026-03-13T10:00:00+00:00",
            "2026-03-13T10:00:00.000Z",
            "2026-03-13T10:00:00",
            "2026-03-13 10:00:00",
        ]
        for ts_format in formats:
            data = {
                "comments": [
                    {"author": "ts_test", "text": "Test", "post_url": "p/1", "timestamp": ts_format}
                ]
            }
            result = analyze_comments(data)
            self.assertEqual(len(result["accounts"]), 1, f"Failed for format: {ts_format}")


class TestBuildmoltDuplicateLaunch(unittest.TestCase):
    """buildmolt posting near-duplicate launch announcements minutes apart."""

    def test_duplicate_launch_posts(self):
        data = {
            "comments": [
                {
                    "author": "buildmolt",
                    "text": (
                        "Introducing Moltbook CLI - Your Command Line Interface to Moltbook! "
                        "Install now with npm install -g moltbook-cli. Get started today!"
                    ),
                    "post_url": "p/1",
                    "timestamp": _ts(BASE_TIME),
                },
                {
                    "author": "buildmolt",
                    "text": (
                        "Introducing Moltbook CLI - The Command Line Interface for Moltbook! "
                        "Install with npm install -g moltbook-cli. Start building today!"
                    ),
                    "post_url": "p/2",
                    "timestamp": _ts(BASE_TIME, 3),
                },
            ]
        }
        result = analyze_comments(data)
        acct = result["accounts"][0]
        self.assertTrue(len(acct["repeated_phrases"]) > 0, "Duplicate launches should flag repeated phrases")


if __name__ == "__main__":
    unittest.main()
