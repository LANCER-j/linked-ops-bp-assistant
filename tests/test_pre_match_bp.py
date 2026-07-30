from __future__ import annotations

import unittest

from bp_assistant.core import (
    MatchConfig,
    MatchRules,
    Operator,
    PLAYER_A,
    PLAYER_B,
    RuleError,
)
from bp_assistant.pre_match_bp import (
    MODE_BAN,
    MODE_BLUE,
    MODE_RED,
    PreMatchBpState,
)


def operator(index: int, branch: str = "尖兵") -> Operator:
    return Operator(
        operator_id=f"op-{index}",
        name=f"干员{index}",
        rarity=6,
        profession="先锋",
        branch=branch,
    )


class PreMatchBpStateTests(unittest.TestCase):
    def test_import_merges_host_bans_and_excludes_global_bans(self) -> None:
        config = MatchConfig(
            match_id="match-1",
            title="测试赛",
            player_a_name="蓝选手",
            player_b_name="红选手",
            rules=MatchRules(),
            global_banned_operator_ids=["op-1"],
            global_banned_branches=["领主"],
            host_banned_operator_ids={
                PLAYER_A: ["op-1", "op-2", "op-4"],
                PLAYER_B: ["op-2", "op-3"],
            },
            host_banned_branches={
                PLAYER_A: ["领主", "尖兵"],
                PLAYER_B: ["术士"],
            },
        )
        state = PreMatchBpState()
        operators = {
            "op-1": operator(1),
            "op-2": operator(2),
            "op-3": operator(3),
            "op-4": operator(4, "领主"),
        }
        state.apply_config(config, operators)
        self.assertEqual(state.blue_name, "蓝选手")
        self.assertEqual(state.red_name, "红选手")
        self.assertEqual(state.player_banned_operator_ids, ["op-2", "op-3"])
        self.assertEqual(state.player_banned_branches, {"尖兵", "术士"})

    def test_ban_and_pick_counts_are_unlimited(self) -> None:
        state = PreMatchBpState()
        for index in range(30):
            state.add(MODE_BAN, operator(index))
        self.assertEqual(len(state.player_banned_operator_ids), 30)

        state = PreMatchBpState()
        for index in range(30):
            state.add(MODE_BLUE, operator(index))
        self.assertEqual(len(state.blue_pick_ids), 30)

    def test_pick_state_affects_other_modes(self) -> None:
        state = PreMatchBpState()
        target = operator(1)
        state.add(MODE_BLUE, target)
        with self.assertRaises(RuleError):
            state.add(MODE_RED, target)
        with self.assertRaises(RuleError):
            state.add(MODE_BAN, target)

    def test_global_and_player_bans_block_pick(self) -> None:
        target = operator(1)
        state = PreMatchBpState(global_banned_operator_ids={target.operator_id})
        with self.assertRaises(RuleError):
            state.add(MODE_BLUE, target)

        state = PreMatchBpState()
        state.add(MODE_BAN, target)
        with self.assertRaises(RuleError):
            state.add(MODE_RED, target)


if __name__ == "__main__":
    unittest.main()
