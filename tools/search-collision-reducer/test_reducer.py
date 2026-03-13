"""
Tests for the search collision reducer.

Covers:
- All 3 sample inputs from the task board
- Exact query match in body outranks username-only collision
- seen_authors get novelty penalty
- Pure collision bait gets keep=false
- Output format matches spec
- Edge cases (empty results, empty query, all seen authors)
- JSON serialization round-trip
- Scoring component unit tests
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reducer import (
    compute_collision,
    compute_novelty,
    compute_relevance,
    load_rules,
    reduce_collisions,
    score_result,
    tokenize_query,
    tokenize_username,
)

RULES = load_rules()


class TestTokenization(unittest.TestCase):

    def test_query_tokenize_hyphenated(self):
        tokens = tokenize_query("py-clob-client", RULES["stop_words"])
        self.assertEqual(tokens, ["py", "clob", "client"])

    def test_query_tokenize_spaces(self):
        tokens = tokenize_query("wallet xray", RULES["stop_words"])
        self.assertEqual(tokens, ["wallet", "xray"])

    def test_query_tokenize_multi_word(self):
        tokens = tokenize_query("prediction market repo", RULES["stop_words"])
        self.assertEqual(tokens, ["prediction", "market", "repo"])

    def test_stop_words_removed(self):
        tokens = tokenize_query("the best market in the world", RULES["stop_words"])
        self.assertNotIn("the", tokens)
        self.assertNotIn("in", tokens)
        self.assertIn("best", tokens)
        self.assertIn("market", tokens)
        self.assertIn("world", tokens)

    def test_empty_query(self):
        tokens = tokenize_query("", RULES["stop_words"])
        self.assertEqual(tokens, [])

    def test_username_tokenize(self):
        tokens = tokenize_username("client_helper_bot")
        self.assertEqual(tokens, ["client", "helper", "bot"])

    def test_username_tokenize_hyphens(self):
        tokens = tokenize_username("wallet-wizard")
        self.assertEqual(tokens, ["wallet", "wizard"])


class TestRelevanceScoring(unittest.TestCase):

    def test_exact_phrase_in_body(self):
        score = compute_relevance(
            "py-clob-client",
            ["py", "clob", "client"],
            "I used py-clob-client to fill orders on Polymarket CLOB",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["relevance_bonuses"]["exact_phrase_in_body"])

    def test_exact_phrase_in_links(self):
        score = compute_relevance(
            "py-clob-client",
            ["py", "clob", "client"],
            "Check out this library for trading.",
            ["https://github.com/example/py-clob-client"],
            RULES,
        )
        self.assertEqual(score, RULES["relevance_bonuses"]["exact_phrase_in_links"])

    def test_all_tokens_in_body(self):
        score = compute_relevance(
            "wallet xray",
            ["wallet", "xray"],
            "the wallet xray tool traces counterparties across chains",
            [],
            RULES,
        )
        self.assertGreaterEqual(score, RULES["relevance_bonuses"]["all_tokens_in_body"])

    def test_no_tokens_in_body(self):
        score = compute_relevance(
            "py-clob-client",
            ["py", "clob", "client"],
            "Just vibing today, great weather!",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["relevance_bonuses"]["no_tokens_in_body"])

    def test_some_tokens_in_body(self):
        score = compute_relevance(
            "prediction market repo",
            ["prediction", "market", "repo"],
            "The market is looking good today.",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["relevance_bonuses"]["some_tokens_in_body"])


class TestCollisionScoring(unittest.TestCase):

    def test_full_username_collision(self):
        """client_helper_bot has 'client' in username but body has nothing about py-clob-client."""
        score = compute_collision(
            ["py", "clob", "client"],
            "client_helper_bot",
            "Hey everyone! Hope you're having a great day. Let's build something cool!",
            [],
            RULES,
        )
        self.assertGreaterEqual(score, RULES["collision_scores"]["some_tokens_username_only"])

    def test_all_tokens_username_only(self):
        """wallet_xray_bot username matches all tokens but body is unrelated."""
        score = compute_collision(
            ["wallet", "xray"],
            "wallet_xray_bot",
            "Just had a great lunch at this new place downtown.",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["collision_scores"]["all_tokens_username_only"])

    def test_no_collision(self):
        """Tokens are in the body, not just the username."""
        score = compute_collision(
            ["py", "clob", "client"],
            "jaris_trader",
            "Used py-clob-client to place orders on the CLOB. Client fills were good.",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["collision_scores"]["no_username_overlap"])

    def test_no_collision_different_username(self):
        score = compute_collision(
            ["wallet", "xray"],
            "research_bot",
            "wallet xray tool is great for tracing counterparties",
            [],
            RULES,
        )
        self.assertEqual(score, RULES["collision_scores"]["no_username_overlap"])


class TestNoveltyScoring(unittest.TestCase):

    def test_fresh_author(self):
        score = compute_novelty("NewAuthor", "some text", [], ["query"], [], RULES)
        self.assertEqual(score, RULES["novelty_scores"]["fresh_author"])

    def test_seen_author_penalty(self):
        score = compute_novelty(
            "Jaris", "just chatting about stuff", ["Jaris"], ["polymarket"], [], RULES
        )
        self.assertLess(score, RULES["novelty_scores"]["fresh_author"])

    def test_seen_author_with_new_content_via_links(self):
        """Seen author with link targets counts as new content."""
        score = compute_novelty(
            "Jaris",
            "Here is my new analysis",
            ["Jaris"],
            ["polymarket"],
            ["https://github.com/jaris/pm-bot"],
            RULES,
        )
        self.assertEqual(score, RULES["novelty_scores"]["seen_author_new_content"])

    def test_seen_author_with_signal_markers(self):
        """Seen author with signal markers (API, CLOB, etc.) in body counts as new."""
        score = compute_novelty(
            "Jaris",
            "Here is my new CLOB analysis with funding rate data and API endpoint",
            ["Jaris"],
            ["polymarket", "funding"],
            [],
            RULES,
        )
        self.assertEqual(score, RULES["novelty_scores"]["seen_author_new_content"])

    def test_seen_author_query_tokens_only_is_stale(self):
        """Seen author whose body only contains query tokens is NOT new content."""
        score = compute_novelty(
            "Jaris",
            "The prediction market space is evolving. Keep watching.",
            ["Jaris"],
            ["prediction", "market", "repo"],
            [],
            RULES,
        )
        self.assertEqual(score, RULES["novelty_scores"]["seen_author_no_new_content"])

    def test_seen_author_no_new_content(self):
        score = compute_novelty(
            "Jaris", "Good morning everyone!", ["Jaris"], ["polymarket"], [], RULES
        )
        self.assertEqual(score, RULES["novelty_scores"]["seen_author_no_new_content"])

    def test_case_insensitive_seen(self):
        score = compute_novelty("jaris", "hello", ["Jaris"], ["test"], [], RULES)
        self.assertLess(score, RULES["novelty_scores"]["fresh_author"])


# ── Sample input 1: py-clob-client ──────────────────────────────────

SAMPLE_1 = {
    "query": "py-clob-client",
    "results": [
        {
            "author": "client_helper_bot",
            "text": "Hey everyone! Just dropping in to say hi. Love this community!",
            "url": "https://moltbook.com/post/aaa1",
            "link_targets": [],
        },
        {
            "author": "generic_client_acc",
            "text": "Check out my new client management tool! It handles all your needs.",
            "url": "https://moltbook.com/post/aaa2",
            "link_targets": [],
        },
        {
            "author": "jaris_trader",
            "text": (
                "Placed a buy NO at $0.22 order using py-clob-client → filled at $0.99 "
                "because that was the only ask available. The CLOB fills were terrible. "
                "if ask-bid spread >20%, skip the market."
            ),
            "url": "https://moltbook.com/post/aaa3",
            "link_targets": ["https://github.com/Polymarket/py-clob-client"],
        },
    ],
    "seen_authors": [],
}


class TestSample1PyClobClient(unittest.TestCase):

    def test_exact_match_outranks_collision(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        ranked = result["ranked_results"]
        jaris = next(r for r in ranked if r["author"] == "jaris_trader")
        client_bot = next(r for r in ranked if r["author"] == "client_helper_bot")
        generic = next(r for r in ranked if r["author"] == "generic_client_acc")

        self.assertGreater(jaris["relevance_score"], client_bot["relevance_score"])
        self.assertGreater(jaris["relevance_score"], generic["relevance_score"])

    def test_jaris_is_kept(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        jaris = next(r for r in result["ranked_results"] if r["author"] == "jaris_trader")
        self.assertTrue(jaris["keep"])

    def test_collision_bots_discarded(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        client_bot = next(
            r for r in result["ranked_results"] if r["author"] == "client_helper_bot"
        )
        self.assertFalse(client_bot["keep"])
        self.assertIn("collision", client_bot["reason"].lower())

    def test_jaris_ranks_first(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        self.assertEqual(result["ranked_results"][0]["author"], "jaris_trader")

    def test_summary_counts(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        self.assertGreaterEqual(result["summary"]["discarded_collisions"], 1)


# ── Sample input 2: wallet xray ─────────────────────────────────────

SAMPLE_2 = {
    "query": "wallet xray",
    "results": [
        {"author": "wallet_wizard", "text": "GM! Building cool stuff.", "url": "https://moltbook.com/post/bbb1", "link_targets": []},
        {"author": "wallet_tracker_v2", "text": "Tracking your portfolio? We got you!", "url": "https://moltbook.com/post/bbb2", "link_targets": []},
        {"author": "crypto_wallet_bot", "text": "Secure your assets with our tips!", "url": "https://moltbook.com/post/bbb3", "link_targets": []},
        {"author": "wallet_agent_x", "text": "AI-powered wallet management coming soon.", "url": "https://moltbook.com/post/bbb4", "link_targets": []},
        {"author": "walletwhale", "text": "Big moves today! LFG!", "url": "https://moltbook.com/post/bbb5", "link_targets": []},
        {"author": "digital_wallet_pro", "text": "New features dropping next week.", "url": "https://moltbook.com/post/bbb6", "link_targets": []},
        {"author": "wallet_ninja_3", "text": "Stay safe out there, fam.", "url": "https://moltbook.com/post/bbb7", "link_targets": []},
        {"author": "hot_wallet_handler", "text": "Another day, another chain.", "url": "https://moltbook.com/post/bbb8", "link_targets": []},
        {
            "author": "chain_analyst",
            "text": (
                "Built a wallet xray tool that traces counterparty flow across 4 chains. "
                "Tracing counterparties reveals cluster patterns in prediction market wallets. "
                "Dashboard: https://dune.com/analyst/wallet-xray"
            ),
            "url": "https://moltbook.com/post/bbb9",
            "link_targets": ["https://dune.com/analyst/wallet-xray"],
        },
    ],
    "seen_authors": [],
}


class TestSample2WalletXray(unittest.TestCase):

    def test_real_post_outranks_wallet_names(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        ranked = result["ranked_results"]
        analyst = next(r for r in ranked if r["author"] == "chain_analyst")

        wallet_bots = [r for r in ranked if r["author"] != "chain_analyst"]
        for bot in wallet_bots:
            self.assertGreater(
                analyst["relevance_score"], bot["relevance_score"],
                f"chain_analyst should outrank {bot['author']}",
            )

    def test_chain_analyst_ranks_first(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        self.assertEqual(result["ranked_results"][0]["author"], "chain_analyst")

    def test_chain_analyst_kept(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        analyst = next(r for r in result["ranked_results"] if r["author"] == "chain_analyst")
        self.assertTrue(analyst["keep"])

    def test_wallet_collision_bots_mostly_discarded(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        wallet_bots = [
            r for r in result["ranked_results"]
            if r["author"] != "chain_analyst"
        ]
        discarded = [r for r in wallet_bots if not r["keep"]]
        self.assertGreaterEqual(len(discarded), 6, "Most wallet-name bots should be discarded")

    def test_summary_collision_count(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        self.assertGreaterEqual(result["summary"]["discarded_collisions"], 5)


# ── Sample input 3: prediction market repo ──────────────────────────

SAMPLE_3 = {
    "query": "prediction market repo",
    "results": [
        {
            "author": "Jaris",
            "text": "The prediction market space is evolving. Keep watching.",
            "url": "https://moltbook.com/post/ccc1",
            "link_targets": [],
        },
        {
            "author": "Lona",
            "text": "Our prediction market tools are getting better every day.",
            "url": "https://moltbook.com/post/ccc2",
            "link_targets": [],
        },
        {
            "author": "Jaris",
            "text": "More thoughts on the prediction market landscape.",
            "url": "https://moltbook.com/post/ccc3",
            "link_targets": [],
        },
        {
            "author": "fresh_dev_2026",
            "text": (
                "Just published our prediction market repo with full CLOB integration. "
                "Repo: https://github.com/fresh_dev/pm-clob-bot — includes funding rate "
                "divergence detection and automated YES/NO arbitrage."
            ),
            "url": "https://moltbook.com/post/ccc4",
            "link_targets": ["https://github.com/fresh_dev/pm-clob-bot"],
        },
    ],
    "seen_authors": ["Jaris", "Lona"],
}


class TestSample3PredictionMarketRepo(unittest.TestCase):

    def test_fresh_author_with_repo_ranks_first(self):
        result = reduce_collisions(SAMPLE_3, RULES)
        self.assertEqual(result["ranked_results"][0]["author"], "fresh_dev_2026")

    def test_fresh_author_kept(self):
        result = reduce_collisions(SAMPLE_3, RULES)
        fresh = next(r for r in result["ranked_results"] if r["author"] == "fresh_dev_2026")
        self.assertTrue(fresh["keep"])

    def test_seen_authors_penalized(self):
        result = reduce_collisions(SAMPLE_3, RULES)
        fresh = next(r for r in result["ranked_results"] if r["author"] == "fresh_dev_2026")
        jaris_entries = [r for r in result["ranked_results"] if r["author"] == "Jaris"]
        for j in jaris_entries:
            self.assertGreater(fresh["novelty_score"], j["novelty_score"])

    def test_seen_authors_get_lower_novelty(self):
        result = reduce_collisions(SAMPLE_3, RULES)
        for r in result["ranked_results"]:
            if r["author"] in ("Jaris", "Lona"):
                self.assertLess(r["novelty_score"], RULES["novelty_scores"]["fresh_author"])

    def test_summary_discarded_seen(self):
        result = reduce_collisions(SAMPLE_3, RULES)
        self.assertGreaterEqual(result["summary"]["discarded_seen"], 1)


# ── Output format compliance ────────────────────────────────────────

class TestOutputFormat(unittest.TestCase):

    def test_top_level_keys(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        self.assertIn("ranked_results", result)
        self.assertIn("summary", result)

    def test_summary_keys(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        summary = result["summary"]
        self.assertIn("discarded_collisions", summary)
        self.assertIn("discarded_seen", summary)
        self.assertIsInstance(summary["discarded_collisions"], int)
        self.assertIsInstance(summary["discarded_seen"], int)

    def test_result_entry_keys(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        for entry in result["ranked_results"]:
            self.assertIn("author", entry)
            self.assertIn("url", entry)
            self.assertIn("relevance_score", entry)
            self.assertIn("collision_score", entry)
            self.assertIn("novelty_score", entry)
            self.assertIn("keep", entry)
            self.assertIn("reason", entry)

    def test_score_ranges(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        for entry in result["ranked_results"]:
            self.assertGreaterEqual(entry["relevance_score"], 0.0)
            self.assertLessEqual(entry["relevance_score"], 1.0)
            self.assertGreaterEqual(entry["collision_score"], 0.0)
            self.assertLessEqual(entry["collision_score"], 1.0)
            self.assertGreaterEqual(entry["novelty_score"], 0.0)
            self.assertLessEqual(entry["novelty_score"], 1.0)

    def test_keep_is_bool(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        for entry in result["ranked_results"]:
            self.assertIsInstance(entry["keep"], bool)

    def test_reason_is_string(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        for entry in result["ranked_results"]:
            self.assertIsInstance(entry["reason"], str)
            self.assertTrue(len(entry["reason"]) > 0)


# ── Edge cases ──────────────────────────────────────────────────────

class TestEdgeCases(unittest.TestCase):

    def test_empty_results(self):
        data = {"query": "test", "results": [], "seen_authors": []}
        result = reduce_collisions(data, RULES)
        self.assertEqual(result["ranked_results"], [])
        self.assertEqual(result["summary"]["discarded_collisions"], 0)
        self.assertEqual(result["summary"]["discarded_seen"], 0)

    def test_empty_query(self):
        data = {
            "query": "",
            "results": [
                {"author": "test_user", "text": "Hello world", "url": "http://x.com/1", "link_targets": []},
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        self.assertEqual(len(result["ranked_results"]), 1)

    def test_all_seen_authors(self):
        data = {
            "query": "polymarket",
            "results": [
                {"author": "Alice", "text": "polymarket is cool", "url": "http://x.com/1", "link_targets": []},
                {"author": "Bob", "text": "I like polymarket too", "url": "http://x.com/2", "link_targets": []},
            ],
            "seen_authors": ["Alice", "Bob"],
        }
        result = reduce_collisions(data, RULES)
        for r in result["ranked_results"]:
            self.assertLess(r["novelty_score"], RULES["novelty_scores"]["fresh_author"])

    def test_single_result(self):
        data = {
            "query": "CLOB",
            "results": [
                {"author": "trader", "text": "CLOB order book is thin", "url": "http://x.com/1", "link_targets": []},
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        self.assertEqual(len(result["ranked_results"]), 1)
        self.assertTrue(result["ranked_results"][0]["keep"])

    def test_missing_link_targets(self):
        """Results without link_targets key should still work."""
        data = {
            "query": "test query",
            "results": [
                {"author": "user1", "text": "test query content", "url": "http://x.com/1"},
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        self.assertEqual(len(result["ranked_results"]), 1)

    def test_query_with_only_stop_words(self):
        data = {
            "query": "the in a",
            "results": [
                {"author": "user1", "text": "something", "url": "http://x.com/1", "link_targets": []},
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        self.assertEqual(len(result["ranked_results"]), 1)


# ── JSON serialization round-trip ───────────────────────────────────

class TestJsonRoundTrip(unittest.TestCase):

    def test_serialize_deserialize(self):
        result = reduce_collisions(SAMPLE_1, RULES)
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)

        self.assertEqual(len(deserialized["ranked_results"]), len(result["ranked_results"]))
        self.assertEqual(deserialized["summary"], result["summary"])

        for orig, rt in zip(result["ranked_results"], deserialized["ranked_results"]):
            self.assertEqual(orig["author"], rt["author"])
            self.assertEqual(orig["url"], rt["url"])
            self.assertAlmostEqual(orig["relevance_score"], rt["relevance_score"])
            self.assertAlmostEqual(orig["collision_score"], rt["collision_score"])
            self.assertAlmostEqual(orig["novelty_score"], rt["novelty_score"])
            self.assertEqual(orig["keep"], rt["keep"])
            self.assertEqual(orig["reason"], rt["reason"])

    def test_round_trip_all_samples(self):
        for sample in [SAMPLE_1, SAMPLE_2, SAMPLE_3]:
            result = reduce_collisions(sample, RULES)
            self.assertEqual(json.loads(json.dumps(result)), result)


# ── Collision bait detection ────────────────────────────────────────

class TestCollisionBaitKeepFalse(unittest.TestCase):

    def test_pure_username_collision_is_not_kept(self):
        """A result where the ONLY match is the username must be keep=false."""
        data = {
            "query": "market making agent",
            "results": [
                {
                    "author": "market_maker_agent",
                    "text": "Good morning! Beautiful day for building!",
                    "url": "https://moltbook.com/post/ddd1",
                    "link_targets": [],
                },
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        entry = result["ranked_results"][0]
        self.assertFalse(entry["keep"])
        self.assertIn("collision", entry["reason"].lower())

    def test_marketing_junk_collision(self):
        """Query 'market making agent' hitting generic marketing post."""
        data = {
            "query": "market making agent",
            "results": [
                {
                    "author": "marketing_guru",
                    "text": "Our marketing strategy is killing it! Growth agent metrics are up 200%.",
                    "url": "https://moltbook.com/post/ddd2",
                    "link_targets": [],
                },
                {
                    "author": "mm_builder",
                    "text": (
                        "Deployed a market making agent on Polymarket. "
                        "The agent places limit orders around the mid-price on the CLOB. "
                        "Repo: https://github.com/mm/pm-maker"
                    ),
                    "url": "https://moltbook.com/post/ddd3",
                    "link_targets": ["https://github.com/mm/pm-maker"],
                },
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        mm = next(r for r in result["ranked_results"] if r["author"] == "mm_builder")
        guru = next(r for r in result["ranked_results"] if r["author"] == "marketing_guru")
        self.assertTrue(mm["keep"])
        self.assertGreater(mm["relevance_score"], guru["relevance_score"])

    def test_explicit_reason_on_collision_bait(self):
        data = {
            "query": "wallet xray",
            "results": [
                {
                    "author": "wallet_xray_agent",
                    "text": "Loving the vibes today! Great community!",
                    "url": "https://moltbook.com/post/eee1",
                    "link_targets": [],
                },
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        entry = result["ranked_results"][0]
        self.assertFalse(entry["keep"])
        self.assertIn("collision", entry["reason"].lower())


# ── Ranking order tests ─────────────────────────────────────────────

class TestRankingOrder(unittest.TestCase):

    def test_results_sorted_by_combined_score(self):
        result = reduce_collisions(SAMPLE_2, RULES)
        ranked = result["ranked_results"]
        scores = [
            r["relevance_score"] - r["collision_score"] + r["novelty_score"]
            for r in ranked
        ]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_high_relevance_beats_collision(self):
        """Even if there's some collision overlap, high relevance wins."""
        data = {
            "query": "wallet xray",
            "results": [
                {
                    "author": "wallet_researcher",
                    "text": "My wallet xray analysis shows cluster patterns in prediction markets.",
                    "url": "https://moltbook.com/post/fff1",
                    "link_targets": [],
                },
                {
                    "author": "wallet_fun",
                    "text": "Having fun with crypto today!",
                    "url": "https://moltbook.com/post/fff2",
                    "link_targets": [],
                },
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        researcher = next(r for r in result["ranked_results"] if r["author"] == "wallet_researcher")
        fun = next(r for r in result["ranked_results"] if r["author"] == "wallet_fun")
        self.assertTrue(researcher["keep"])
        self.assertGreater(researcher["relevance_score"], fun["relevance_score"])


# ── Signal boost patterns ───────────────────────────────────────────

class TestSignalBoost(unittest.TestCase):

    def test_repo_link_boosts_relevance(self):
        data = {
            "query": "prediction market",
            "results": [
                {
                    "author": "dev1",
                    "text": "Here is my prediction market bot.",
                    "url": "https://moltbook.com/post/ggg1",
                    "link_targets": ["https://github.com/dev1/pm-bot"],
                },
                {
                    "author": "dev2",
                    "text": "prediction market is interesting to watch",
                    "url": "https://moltbook.com/post/ggg2",
                    "link_targets": [],
                },
            ],
            "seen_authors": [],
        }
        result = reduce_collisions(data, RULES)
        dev1 = next(r for r in result["ranked_results"] if r["author"] == "dev1")
        dev2 = next(r for r in result["ranked_results"] if r["author"] == "dev2")
        self.assertTrue(dev1["keep"])
        self.assertTrue(dev2["keep"])

    def test_link_target_with_query_boosts(self):
        score = compute_relevance(
            "py-clob-client",
            ["py", "clob", "client"],
            "Check out this trading library.",
            ["https://pypi.org/project/py-clob-client/"],
            RULES,
        )
        self.assertGreaterEqual(score, RULES["relevance_bonuses"]["exact_phrase_in_links"])


# ── Seen author + collision combo ───────────────────────────────────

class TestSeenPlusCollision(unittest.TestCase):

    def test_seen_author_with_collision_double_penalty(self):
        data = {
            "query": "wallet xray",
            "results": [
                {
                    "author": "wallet_bot",
                    "text": "GM everyone! Love building here.",
                    "url": "https://moltbook.com/post/hhh1",
                    "link_targets": [],
                },
            ],
            "seen_authors": ["wallet_bot"],
        }
        result = reduce_collisions(data, RULES)
        entry = result["ranked_results"][0]
        self.assertFalse(entry["keep"])
        self.assertGreater(entry["collision_score"], 0)
        self.assertLess(entry["novelty_score"], RULES["novelty_scores"]["fresh_author"])


# ── Rules loading ───────────────────────────────────────────────────

class TestRulesLoading(unittest.TestCase):

    def test_default_rules_load(self):
        rules = load_rules()
        self.assertIn("scoring_weights", rules)
        self.assertIn("thresholds", rules)
        self.assertIn("stop_words", rules)
        self.assertIn("relevance_bonuses", rules)
        self.assertIn("collision_scores", rules)
        self.assertIn("novelty_scores", rules)

    def test_rules_weights_sum_reasonable(self):
        rules = load_rules()
        w = rules["scoring_weights"]
        self.assertAlmostEqual(
            w["relevance"] + w["collision_penalty"] + w["novelty"], 1.0
        )


if __name__ == "__main__":
    unittest.main()
