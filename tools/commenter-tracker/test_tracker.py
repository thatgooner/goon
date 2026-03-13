"""
Tests for commenter pattern tracker.

Covers testable_acceptance from the task board:
- hype_bot_99 must produce spam_score > 0.7
- legit_builder must produce spam_score < 0.3
- repeated_phrases must be non-empty when the same phrase appears in 2+ comments from same author

Also covers patterns from gooner's daily research notes:
- simoncaleb_openclaw_bot repeated meta-question walls
- Editor-in-Chief thread hijack promo
- ClawV6 generic praise filler
- Coordinated burst detection
- Mixed account behaviors
"""

import json
import unittest
from pathlib import Path

from tracker import analyze, _find_repeated_phrases, _find_burst_windows, _parse_ts, _token_similarity, _tokenize


class TestTaskBoardAcceptance(unittest.TestCase):
    """Tests matching the exact acceptance criteria from the task board."""

    def setUp(self):
        self.hype_bot_data = {
            "comments": [
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:04:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:06:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/5", "timestamp": "2026-03-13T02:08:00Z"},
            ]
        }
        self.legit_data = {
            "comments": [
                {
                    "author": "legit_builder",
                    "text": "I tested this against the polymarket CLOB API — the spread filter at 20% catches most illiquid markets. Here's my fork: github.com/legit/pm-filter",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T02:00:00Z",
                },
                {
                    "author": "legit_builder",
                    "text": "The funding rate divergence strategy needs a different approach for sub-$50k markets. I ran backtests on 200 markets and the win rate drops below 40% when volume is under 10k. Repo: github.com/legit/funding-bt",
                    "post_url": "https://moltbook.com/post/6",
                    "timestamp": "2026-03-15T14:30:00Z",
                },
            ]
        }

    def test_hype_bot_spam_score_above_07(self):
        """Task board: hype_bot_99 must produce spam_score > 0.7"""
        result = analyze(self.hype_bot_data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertIn("hype_bot_99", accounts)
        self.assertGreater(accounts["hype_bot_99"]["spam_score"], 0.7,
                           f"hype_bot_99 spam_score={accounts['hype_bot_99']['spam_score']} should be > 0.7")

    def test_legit_builder_spam_score_below_03(self):
        """Task board: legit_builder must produce spam_score < 0.3"""
        result = analyze(self.legit_data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertIn("legit_builder", accounts)
        self.assertLess(accounts["legit_builder"]["spam_score"], 0.3,
                        f"legit_builder spam_score={accounts['legit_builder']['spam_score']} should be < 0.3")

    def test_repeated_phrases_nonempty_for_duplicates(self):
        """Task board: repeated_phrases must be non-empty when same phrase appears in 2+ comments."""
        result = analyze(self.hype_bot_data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertGreater(len(accounts["hype_bot_99"]["repeated_phrases"]), 0,
                           "repeated_phrases should be non-empty for exact duplicate comments")

    def test_legit_no_repeated_phrases(self):
        """legit_builder's distinct comments should not produce repeated phrases."""
        result = analyze(self.legit_data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertEqual(len(accounts["legit_builder"]["repeated_phrases"]), 0)


class TestBothAccountsTogether(unittest.TestCase):
    """Test with both accounts in the same input, as the task board implies."""

    def test_mixed_input(self):
        data = {
            "comments": [
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:04:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:06:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/5", "timestamp": "2026-03-13T02:08:00Z"},
                {
                    "author": "legit_builder",
                    "text": "I tested this against the polymarket CLOB API — the spread filter at 20% catches most illiquid markets. Here's my fork: github.com/legit/pm-filter",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T02:00:00Z",
                },
                {
                    "author": "legit_builder",
                    "text": "The funding rate divergence strategy needs a different approach for sub-$50k markets. I ran backtests on 200 markets and the win rate drops below 40% when volume is under 10k. Repo: github.com/legit/funding-bt",
                    "post_url": "https://moltbook.com/post/6",
                    "timestamp": "2026-03-15T14:30:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}

        self.assertGreater(accounts["hype_bot_99"]["spam_score"], 0.7)
        self.assertLess(accounts["legit_builder"]["spam_score"], 0.3)
        self.assertGreater(len(accounts["hype_bot_99"]["repeated_phrases"]), 0)


class TestBurstDetection(unittest.TestCase):

    def test_burst_window_detected(self):
        """5 comments in 10 minutes should produce at least one burst window."""
        data = {
            "comments": [
                {"author": "spammer", "text": "Check this out!", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "spammer", "text": "Check this out!", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "spammer", "text": "Check this out!", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "spammer", "text": "Check this out!", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:03:00Z"},
                {"author": "spammer", "text": "Check this out!", "post_url": "https://moltbook.com/post/5", "timestamp": "2026-03-13T02:04:00Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertGreater(len(accounts["spammer"]["burst_windows"]), 0)

    def test_no_burst_for_spread_comments(self):
        """Comments spread over days should not produce burst windows."""
        data = {
            "comments": [
                {"author": "slow_poster", "text": "Interesting analysis here", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-10T10:00:00Z"},
                {"author": "slow_poster", "text": "Different perspective on this", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-12T15:00:00Z"},
                {"author": "slow_poster", "text": "Follow-up with my testing results", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-14T09:00:00Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertEqual(len(accounts["slow_poster"]["burst_windows"]), 0)


class TestRepeatedPhrases(unittest.TestCase):

    def test_exact_duplicates_detected(self):
        comments = [
            {"author": "bot", "text": "Great work!", "post_url": "a", "timestamp": "2026-03-13T02:00:00Z"},
            {"author": "bot", "text": "Great work!", "post_url": "b", "timestamp": "2026-03-13T02:01:00Z"},
        ]
        repeated = _find_repeated_phrases(comments, 0.85)
        self.assertGreater(len(repeated), 0)

    def test_similar_phrases_detected(self):
        comments = [
            {"author": "bot", "text": "This is amazing incredible work from you", "post_url": "a", "timestamp": "2026-03-13T02:00:00Z"},
            {"author": "bot", "text": "This is amazing incredible work from the team", "post_url": "b", "timestamp": "2026-03-13T02:01:00Z"},
        ]
        repeated = _find_repeated_phrases(comments, 0.75)
        self.assertGreater(len(repeated), 0)

    def test_different_phrases_not_detected(self):
        comments = [
            {"author": "real", "text": "I tested the CLOB API and found a spread issue at 20% threshold", "post_url": "a", "timestamp": "2026-03-13T02:00:00Z"},
            {"author": "real", "text": "The funding rate divergence strategy needs backtesting on 200 markets", "post_url": "b", "timestamp": "2026-03-13T02:01:00Z"},
        ]
        repeated = _find_repeated_phrases(comments, 0.85)
        self.assertEqual(len(repeated), 0)

    def test_single_comment_no_repeats(self):
        comments = [
            {"author": "solo", "text": "Just one comment", "post_url": "a", "timestamp": "2026-03-13T02:00:00Z"},
        ]
        repeated = _find_repeated_phrases(comments, 0.85)
        self.assertEqual(len(repeated), 0)


class TestGonerPatterns(unittest.TestCase):
    """Test patterns observed in gooner's daily research notes."""

    def test_simoncaleb_meta_question_walls(self):
        """simoncaleb_openclaw_bot repeated long-form 'insightful question' pattern."""
        data = {
            "comments": [
                {
                    "author": "simoncaleb_openclaw_bot",
                    "text": "What are your thoughts on how this could be applied to broader market dynamics? Have you considered the implications for cross-chain interoperability? I wonder if this framework could be extended to handle edge cases in high-volatility scenarios? Isn't it fascinating how the convergence of these technologies creates new paradigms?",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T02:10:00Z",
                },
                {
                    "author": "simoncaleb_openclaw_bot",
                    "text": "What do you think about the long-term viability of this approach? Have you considered how institutional adoption might change the dynamics? I wonder whether the current infrastructure can support this at scale? Don't you agree that the decentralized nature adds complexity?",
                    "post_url": "https://moltbook.com/post/2",
                    "timestamp": "2026-03-13T02:12:00Z",
                },
                {
                    "author": "simoncaleb_openclaw_bot",
                    "text": "How would you compare this methodology to traditional approaches? Could this be the missing piece for automated market making? What if we combined this with sentiment analysis? Isn't it interesting how these patterns emerge across different market conditions?",
                    "post_url": "https://moltbook.com/post/3",
                    "timestamp": "2026-03-13T02:14:00Z",
                },
                {
                    "author": "simoncaleb_openclaw_bot",
                    "text": "Have you thought about how this intersects with regulatory considerations? What are the implications for smaller participants? I wonder if there is a threshold effect at play here? Don't you think the composability angle deserves more exploration?",
                    "post_url": "https://moltbook.com/post/4",
                    "timestamp": "2026-03-13T02:16:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        acct = accounts["simoncaleb_openclaw_bot"]
        self.assertGreater(acct["spam_score"], 0.4, "Meta-question wall spammer should score moderately high")
        self.assertGreater(len(acct["burst_windows"]), 0, "4 comments in 6 minutes should trigger burst")

    def test_editor_in_chief_thread_hijack(self):
        """Editor-in-Chief posting irrelevant promo in technical threads."""
        data = {
            "comments": [
                {
                    "author": "Editor-in-Chief",
                    "text": "You are Invited to Watch Human Culture. Check out finallyoffline.com/rss.xml for daily updates on the intersection of humanity and technology. Subscribe now!",
                    "post_url": "https://moltbook.com/post/clob-execution",
                    "timestamp": "2026-03-13T02:15:00Z",
                },
                {
                    "author": "Editor-in-Chief",
                    "text": "Don't miss our latest edition! Visit finallyoffline.com for curated content. Follow us for more insights into what makes us human. Subscribe to our newsletter!",
                    "post_url": "https://moltbook.com/post/funding-rates",
                    "timestamp": "2026-03-13T02:17:00Z",
                },
                {
                    "author": "Editor-in-Chief",
                    "text": "Human Culture Weekly is live! Check out finallyoffline.com/rss.xml — your daily dose of culture and tech commentary. Subscribe today!",
                    "post_url": "https://moltbook.com/post/market-analysis",
                    "timestamp": "2026-03-13T02:19:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        acct = accounts["Editor-in-Chief"]
        self.assertGreater(acct["spam_score"], 0.5, "Promo thread hijacker should score high")

    def test_clawv6_generic_praise(self):
        """ClawV6 generic daily-thought filler."""
        data = {
            "comments": [
                {
                    "author": "ClawV6",
                    "text": "The community here is incredible. So many brilliant minds working together. #web3 #crypto #learning",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T02:00:00Z",
                },
                {
                    "author": "ClawV6",
                    "text": "Amazing progress everyone! The future of AI is here and we're building it together 🚀💯",
                    "post_url": "https://moltbook.com/post/2",
                    "timestamp": "2026-03-13T02:03:00Z",
                },
                {
                    "author": "ClawV6",
                    "text": "Incredible work from this team! Love seeing the innovation happening here 🔥",
                    "post_url": "https://moltbook.com/post/3",
                    "timestamp": "2026-03-13T02:05:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        acct = accounts["ClawV6"]
        self.assertGreater(acct["spam_score"], 0.5, "Generic praise filler should score moderately high")


class TestOutputFormat(unittest.TestCase):
    """Verify the output format matches the task board spec."""

    def test_output_has_accounts_key(self):
        result = analyze({"comments": []})
        self.assertIn("accounts", result)
        self.assertIsInstance(result["accounts"], list)

    def test_account_fields(self):
        data = {
            "comments": [
                {"author": "test", "text": "Hello", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
            ]
        }
        result = analyze(data)
        acct = result["accounts"][0]
        self.assertIn("author", acct)
        self.assertIn("comment_count", acct)
        self.assertIn("repeated_phrases", acct)
        self.assertIn("touched_posts", acct)
        self.assertIn("burst_windows", acct)
        self.assertIn("spam_score", acct)
        self.assertIsInstance(acct["author"], str)
        self.assertIsInstance(acct["comment_count"], int)
        self.assertIsInstance(acct["repeated_phrases"], list)
        self.assertIsInstance(acct["touched_posts"], list)
        self.assertIsInstance(acct["burst_windows"], list)
        self.assertIsInstance(acct["spam_score"], float)

    def test_spam_score_range(self):
        data = {
            "comments": [
                {"author": "a", "text": "Amazing! 🔥", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "b", "text": "Tested CLOB API at github.com/test/repo with 200 markets backtested", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:00:00Z"},
            ]
        }
        result = analyze(data)
        for acct in result["accounts"]:
            self.assertGreaterEqual(acct["spam_score"], 0.0)
            self.assertLessEqual(acct["spam_score"], 1.0)

    def test_burst_window_fields(self):
        data = {
            "comments": [
                {"author": "fast_poster", "text": "Comment 1", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "fast_poster", "text": "Comment 2", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "fast_poster", "text": "Comment 3", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "fast_poster", "text": "Comment 4", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:03:00Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        bursts = accounts["fast_poster"]["burst_windows"]
        if bursts:
            b = bursts[0]
            self.assertIn("start", b)
            self.assertIn("end", b)
            self.assertIn("count", b)

    def test_touched_posts_correct(self):
        data = {
            "comments": [
                {"author": "multi", "text": "Comment A", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "multi", "text": "Comment B", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "multi", "text": "Comment C", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:02:00Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertEqual(len(accounts["multi"]["touched_posts"]), 2)

    def test_comment_count_correct(self):
        data = {
            "comments": [
                {"author": "counter", "text": "One", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "counter", "text": "Two", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "counter", "text": "Three", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertEqual(accounts["counter"]["comment_count"], 3)

    def test_sorted_by_spam_score_desc(self):
        data = {
            "comments": [
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "hype_bot_99", "text": "Amazing work! 🔥", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "legit_builder", "text": "Tested CLOB API at github.com/test/repo with 200 markets backtested, win rate 40%", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:00:00Z"},
            ]
        }
        result = analyze(data)
        scores = [a["spam_score"] for a in result["accounts"]]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestEdgeCases(unittest.TestCase):

    def test_empty_comments(self):
        result = analyze({"comments": []})
        self.assertEqual(result["accounts"], [])

    def test_single_comment(self):
        data = {
            "comments": [
                {"author": "solo", "text": "Just one comment here", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
            ]
        }
        result = analyze(data)
        self.assertEqual(len(result["accounts"]), 1)
        self.assertEqual(result["accounts"][0]["comment_count"], 1)
        self.assertEqual(result["accounts"][0]["repeated_phrases"], [])
        self.assertEqual(result["accounts"][0]["burst_windows"], [])

    def test_missing_fields_handled(self):
        data = {
            "comments": [
                {"author": "incomplete", "text": "Some text"},
                {"author": "incomplete", "text": "More text"},
            ]
        }
        result = analyze(data)
        self.assertEqual(len(result["accounts"]), 1)

    def test_varied_timestamp_formats(self):
        data = {
            "comments": [
                {"author": "ts_test", "text": "Comment A", "post_url": "a", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "ts_test", "text": "Comment B", "post_url": "b", "timestamp": "2026-03-13T02:01:00+00:00"},
                {"author": "ts_test", "text": "Comment C", "post_url": "c", "timestamp": "2026-03-13 02:02:00"},
            ]
        }
        result = analyze(data)
        self.assertEqual(len(result["accounts"]), 1)
        self.assertEqual(result["accounts"][0]["comment_count"], 3)


class TestTokenSimilarity(unittest.TestCase):

    def test_identical_texts(self):
        tokens = _tokenize("Amazing work!")
        self.assertEqual(_token_similarity(tokens, tokens), 1.0)

    def test_completely_different(self):
        a = _tokenize("polymarket CLOB API testing backtests")
        b = _tokenize("incredible amazing phenomenal brilliant")
        sim = _token_similarity(a, b)
        self.assertLess(sim, 0.3)

    def test_empty_tokens(self):
        self.assertEqual(_token_similarity([], []), 0.0)
        self.assertEqual(_token_similarity(["a"], []), 0.0)


class TestTimestampParsing(unittest.TestCase):

    def test_iso_z(self):
        ts = _parse_ts("2026-03-13T02:00:00Z")
        self.assertIsNotNone(ts)

    def test_iso_offset(self):
        ts = _parse_ts("2026-03-13T02:00:00+00:00")
        self.assertIsNotNone(ts)

    def test_space_format(self):
        ts = _parse_ts("2026-03-13 02:00:00")
        self.assertIsNotNone(ts)

    def test_invalid_returns_none(self):
        ts = _parse_ts("not-a-date")
        self.assertIsNone(ts)


class TestPromoDetection(unittest.TestCase):
    """Promo/solicitation accounts should score higher."""

    def test_promo_spammer(self):
        data = {
            "comments": [
                {
                    "author": "promo_bot",
                    "text": "Check out our amazing new platform! Sign up now at example.com/signup and use code SAVE20 for a discount! Follow me for more tips!",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T02:00:00Z",
                },
                {
                    "author": "promo_bot",
                    "text": "Don't miss this opportunity! Visit our website and subscribe to our newsletter. DM me for exclusive deals!",
                    "post_url": "https://moltbook.com/post/2",
                    "timestamp": "2026-03-13T02:02:00Z",
                },
                {
                    "author": "promo_bot",
                    "text": "Join our community on Telegram at t.me/promogroup! Exclusive airdrops and minting events coming soon. Sign up now!",
                    "post_url": "https://moltbook.com/post/3",
                    "timestamp": "2026-03-13T02:04:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertGreater(accounts["promo_bot"]["spam_score"], 0.5)


class TestCoordinatedSpam(unittest.TestCase):

    def test_ring_of_praise_bots(self):
        """Multiple bots posting the same praise across posts."""
        data = {
            "comments": [
                {"author": "bot_a", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:00Z"},
                {"author": "bot_a", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:00Z"},
                {"author": "bot_a", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:00Z"},
                {"author": "bot_a", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:03:00Z"},
                {"author": "bot_b", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/1", "timestamp": "2026-03-13T02:00:30Z"},
                {"author": "bot_b", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/2", "timestamp": "2026-03-13T02:01:30Z"},
                {"author": "bot_b", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/3", "timestamp": "2026-03-13T02:02:30Z"},
                {"author": "bot_b", "text": "Incredible work! This is the future! 🔥🚀", "post_url": "https://moltbook.com/post/4", "timestamp": "2026-03-13T02:03:30Z"},
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertGreater(accounts["bot_a"]["spam_score"], 0.6)
        self.assertGreater(accounts["bot_b"]["spam_score"], 0.6)


class TestSubstantiveAccounts(unittest.TestCase):

    def test_technical_commenter_low_score(self):
        data = {
            "comments": [
                {
                    "author": "technical_dev",
                    "text": "I forked this repo at github.com/techdev/fork and ran the test suite. The v2.1.3 API endpoint returns 404 on markets with volume under $500. Here's my patch: fix the threshold check in line 142 of clob_client.py",
                    "post_url": "https://moltbook.com/post/1",
                    "timestamp": "2026-03-13T10:00:00Z",
                },
                {
                    "author": "technical_dev",
                    "text": "Backtested the funding rate strategy on 150 markets from dune.com/techdev/funding-rates. Results: 62% win rate on markets above $10k volume, drops to 38% below that threshold. The Sharpe ratio was 0.8 which is mediocre.",
                    "post_url": "https://moltbook.com/post/2",
                    "timestamp": "2026-03-14T15:00:00Z",
                },
            ]
        }
        result = analyze(data)
        accounts = {a["author"]: a for a in result["accounts"]}
        self.assertLess(accounts["technical_dev"]["spam_score"], 0.3)


if __name__ == "__main__":
    unittest.main()
