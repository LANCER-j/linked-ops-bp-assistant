from __future__ import annotations

import unittest

from bp_assistant.core import (
    AuctionItem,
    MatchConfig,
    MatchRules,
    MatchState,
    Operator,
    PlayerSubmission,
    RuleError,
    build_auction,
    dataclass_to_dict,
    make_envelope,
    verify_envelope,
)


class CoreRulesTests(unittest.TestCase):
    def test_auction_timer_defaults_and_validation(self) -> None:
        rules = MatchRules()
        self.assertEqual(20, rules.auction_timer_seconds)
        rules.validate()
        with self.assertRaises(RuleError):
            MatchRules(auction_timer_seconds=0).validate()

    def setUp(self) -> None:
        self.operators = {
            "op_a": Operator("op_a", "甲", 6, "近卫", "无畏者"),
            "op_b": Operator("op_b", "乙", 5, "医疗", "医师"),
            "op_c": Operator("op_c", "丙", 4, "先锋", "尖兵"),
            "op_d": Operator("op_d", "丁", 6, "狙击", "速射手"),
            "ban_a": Operator("ban_a", "禁甲", 5, "辅助", "凝滞师"),
            "ban_b": Operator("ban_b", "禁乙", 5, "特种", "处决者"),
        }
        rules = MatchRules(
            branch_bans_per_player=1,
            operator_bans_per_player=1,
            rounds=1,
            picks_per_round=2,
        )
        self.config = MatchConfig("M-001", "测试赛", "小A", "小B", rules)
        self.a = PlayerSubmission(
            "M-001", "A", "小A", 1, ["领主"], ["ban_a"], ["op_a", "op_b"]
        )
        self.b = PlayerSubmission(
            "M-001", "B", "小B", 1, ["术士"], ["ban_b"], ["op_a", "op_c"]
        )

    def test_duplicate_picks_are_merged(self) -> None:
        items = build_auction(self.config, self.a, self.b, self.operators, seed=42)
        self.assertEqual(3, len(items))
        shared = next(item for item in items if item.operator_id == "op_a")
        self.assertEqual(["A", "B"], shared.nominated_by)
        self.assertEqual(8, shared.starting_price)

    def test_bid_and_score(self) -> None:
        items = build_auction(self.config, self.a, self.b, self.operators, seed=42)
        for index, item in enumerate(items):
            winner = "A" if index < 2 else "B"
            item.place_bid(winner, item.starting_price, self.config.rules)
            item.award()
        state = MatchState(config=self.config, auction_items=items)
        a_items = [item for item in items if item.winner == "A"]
        state.used_operator_ids["A"] = [a_items[0].operator_id]
        score = state.calculate_score("A")
        expected = a_items[0].final_price + a_items[1].final_price / 2
        self.assertEqual(expected, score["total"])

        state.score_adjustments["A"] = -1.5
        adjusted = state.calculate_score("A")
        self.assertEqual(expected, adjusted["base_total"])
        self.assertEqual(-1.5, adjusted["adjustment"])
        self.assertEqual(expected - 1.5, adjusted["total"])

    def test_price_cap_is_enforced(self) -> None:
        item = AuctionItem("op_a", 1, ["A"], 8)
        with self.assertRaises(RuleError):
            item.place_bid("A", 25, self.config.rules)

    def test_score_adjustment_changes_final_winner(self) -> None:
        items = [
            AuctionItem(
                "op_a",
                1,
                ["A"],
                8,
                status="sold",
                winner="A",
                final_price=8,
            ),
            AuctionItem(
                "op_d",
                1,
                ["B"],
                8,
                status="sold",
                winner="B",
                final_price=8,
            ),
        ]
        state = MatchState(config=self.config, auction_items=items)
        state.used_operator_ids = {"A": ["op_a"], "B": ["op_d"]}
        state.perfect_clear = {"A": True, "B": True}
        state.score_adjustments["B"] = 2
        result = state.result()
        self.assertEqual("A", result["winner"])
        self.assertEqual(10, result["B"]["total"])

    def test_leading_player_can_raise_consecutively(self) -> None:
        item = AuctionItem("op_a", 1, ["A"], 8)
        item.place_bid("A", 8, self.config.rules)
        item.place_bid("A", 9, self.config.rules)
        self.assertEqual("A", item.leader)
        self.assertEqual(9, item.current_price)
        self.assertEqual(["A", "A"], [bid.player for bid in item.bids])

    def test_early_pass_then_opponent_bid_auto_awards(self) -> None:
        item = AuctionItem("op_a", 1, ["A"], 8)
        self.assertFalse(item.pass_bid("A"))
        item.place_bid("B", 8, self.config.rules)
        self.assertEqual("sold", item.status)
        self.assertEqual("B", item.winner)

    def test_reauction_resets_price_and_preserves_timeline(self) -> None:
        item = AuctionItem("op_a", 1, ["A"], 8)
        item.place_bid("A", 8, self.config.rules)
        item.award()
        first_bid_timestamp = item.bids[0].timestamp

        item.reset_for_reauction()

        self.assertEqual("pending", item.status)
        self.assertIsNone(item.current_price)
        self.assertIsNone(item.winner)
        self.assertEqual(2, item.attempt)
        self.assertEqual(first_bid_timestamp, item.bids[0].timestamp)
        self.assertEqual(
            ["bid", "sold", "reauction"],
            [event.action for event in item.timeline],
        )

    def test_match_is_not_complete_before_all_configured_rounds(self) -> None:
        rules = MatchRules(
            branch_bans_per_player=1,
            operator_bans_per_player=1,
            rounds=2,
            picks_per_round=2,
        )
        config = MatchConfig("M-003", "两轮测试", "小A", "小B", rules)
        items = [
            AuctionItem("op_a", 1, ["A"], 8),
            AuctionItem("op_b", 1, ["B"], 4),
        ]
        for item in items:
            item.place_bid("A", item.starting_price, rules)
            item.award()
        state = MatchState(config=config, auction_items=items)
        self.assertFalse(state.auction_complete)

    def test_submission_rejects_wrong_pick_count(self) -> None:
        rules = MatchRules(
            branch_bans_per_player=1,
            operator_bans_per_player=1,
            rounds=2,
            picks_per_round=1,
        )
        config = MatchConfig("M-002", "测试", "小A", "小B", rules)
        submission = PlayerSubmission(
            "M-002", "A", "小A", 1, ["领主"], ["ban_a"], ["op_a", "op_b"]
        )
        with self.assertRaises(RuleError):
            submission.validate(config, self.operators)

    def test_submission_rejects_global_and_host_bans(self) -> None:
        config = MatchConfig(
            "M-004",
            "完整 Ban 配置",
            "小A",
            "小B",
            MatchRules(
                branch_bans_per_player=1,
                operator_bans_per_player=1,
                rounds=1,
                picks_per_round=1,
            ),
            global_banned_operator_ids=["op_a"],
            global_banned_branches=["医师"],
            host_banned_branches={"A": ["领主"], "B": ["术士"]},
            host_banned_operator_ids={"A": ["ban_a"], "B": ["ban_b"]},
            bans_finalized=True,
        )
        submission = PlayerSubmission(
            "M-004", "A", "小A", 1, ["领主"], ["ban_a"], ["op_a"]
        )
        with self.assertRaises(RuleError):
            submission.validate(config, self.operators)

    def test_envelope_detects_changes(self) -> None:
        envelope = make_envelope("match_config", dataclass_to_dict(self.config))
        envelope["payload"]["title"] = "被修改"
        with self.assertRaises(RuleError):
            verify_envelope(envelope, "match_config")


if __name__ == "__main__":
    unittest.main()
