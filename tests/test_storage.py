from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from bp_assistant.core import (
    AuctionItem,
    MatchConfig,
    MatchRules,
    MatchState,
    PlayerSubmission,
)
from bp_assistant.storage import (
    load_config,
    load_state,
    load_submission,
    save_config,
    save_state,
    save_submission,
)


class StorageRoundTripTests(unittest.TestCase):
    def test_all_competition_files_round_trip(self) -> None:
        config = MatchConfig(
            "SAVE-1",
            "存档测试",
            "甲方",
            "乙方",
            MatchRules(auction_timer_seconds=35),
            global_banned_operator_ids=["global_1", "global_2"],
            global_banned_branches=["召唤师"],
            host_banned_branches={"A": ["领主"], "B": ["术士"]},
            host_banned_operator_ids={
                "A": ["ban_1", "ban_2", "ban_3", "ban_4"],
                "B": ["ban_5", "ban_6", "ban_7", "ban_8"],
            },
            bans_finalized=True,
        )
        submission = PlayerSubmission(
            match_id="SAVE-1",
            player="A",
            player_name="甲方",
            round_index=1,
            banned_branches=["领主"],
            banned_operator_ids=["ban_1", "ban_2", "ban_3", "ban_4"],
            picks=["op_1", "op_2", "op_3", "op_4", "op_5"],
        )
        item = AuctionItem(
            operator_id="op_1",
            round_index=1,
            nominated_by=["A"],
            starting_price=8,
            status="sold",
            current_price=9,
            leader="A",
            winner="A",
            final_price=9,
        )
        item.record_event("bid", player="A", amount=9)
        item.record_event("sold", player="A", amount=9)
        state = MatchState(config=config, auction_items=[item], auction_seed=123)
        state.submissions["R1:A"] = submission
        state.score_adjustments["A"] = -2.5

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "test.bpmatch"
            submission_path = root / "test.bpselect"
            state_path = root / "test.bprace"
            save_config(config_path, config)
            save_submission(submission_path, submission)
            save_state(state_path, state)

            loaded_config = load_config(config_path)
            self.assertEqual("SAVE-1", loaded_config.match_id)
            self.assertEqual(35, loaded_config.rules.auction_timer_seconds)
            self.assertTrue(loaded_config.bans_finalized)
            self.assertEqual(["global_1", "global_2"], loaded_config.global_banned_operator_ids)
            self.assertEqual(["ban_1", "ban_2", "ban_3", "ban_4"], loaded_config.host_banned_operator_ids["A"])
            self.assertEqual(1, load_submission(submission_path).round_index)
            loaded_state = load_state(state_path)
            self.assertEqual(9, loaded_state.auction_items[0].final_price)
            self.assertIn("R1:A", loaded_state.submissions)
            self.assertEqual(-2.5, loaded_state.score_adjustments["A"])
            self.assertEqual(
                ["bid", "sold"],
                [event.action for event in loaded_state.auction_items[0].timeline],
            )


if __name__ == "__main__":
    unittest.main()
