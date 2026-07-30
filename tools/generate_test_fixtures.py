from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bp_assistant.core import (
    MatchConfig,
    MatchRules,
    MatchState,
    PLAYER_A,
    PLAYER_B,
    PlayerSubmission,
    build_auction_round,
)
from bp_assistant.storage import (
    load_operators,
    save_config,
    save_state,
    save_submission,
)


OUTPUT = ROOT / "测试文件"


def build_submissions(
    config: MatchConfig,
    operators,
    rounds: int,
    candidate_offset: int = 0,
) -> list[PlayerSubmission]:
    branch_names = sorted({operator.branch for operator in operators.values()})
    banned_branches = {
        PLAYER_A: [branch_names[0]],
        PLAYER_B: [branch_names[1]],
    }
    eligible = [
        operator
        for operator in operators.values()
        if operator.branch not in banned_branches[PLAYER_A] + banned_branches[PLAYER_B]
        and operator.branch not in config.global_banned_branches
        and operator.operator_id not in config.global_banned_operator_ids
    ]
    eligible.sort(key=lambda operator: (-operator.rarity, operator.profession, operator.name))
    eligible = eligible[candidate_offset:] + eligible[:candidate_offset]
    banned_ids = {
        PLAYER_A: [operator.operator_id for operator in eligible[:4]],
        PLAYER_B: [operator.operator_id for operator in eligible[4:8]],
    }
    candidates = [
        operator.operator_id
        for operator in eligible[8:]
        if operator.operator_id not in banned_ids[PLAYER_A] + banned_ids[PLAYER_B]
    ]

    submissions: list[PlayerSubmission] = []
    cursor = 0
    for round_index in range(1, rounds + 1):
        block = candidates[cursor : cursor + 9]
        if len(block) < 9:
            raise RuntimeError("测试干员数量不足")
        cursor += 9
        picks = {
            PLAYER_A: block[:5],
            PLAYER_B: [block[4], *block[5:9]],
        }
        for player in (PLAYER_A, PLAYER_B):
            submission = PlayerSubmission(
                match_id=config.match_id,
                player=player,
                player_name=(
                    config.player_a_name if player == PLAYER_A else config.player_b_name
                ),
                round_index=round_index,
                banned_branches=banned_branches[player],
                banned_operator_ids=banned_ids[player],
                picks=picks[player],
            )
            submission.validate(config, operators)
            submissions.append(submission)
    return submissions


def save_suite_files(
    directory: Path,
    config: MatchConfig,
    submissions: list[PlayerSubmission],
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    save_config(directory / "比赛配置.bpmatch", config)
    for submission in submissions:
        save_submission(
            directory
            / f"{submission.player}方_第{submission.round_index}轮.bpselect",
            submission,
        )


def apply_host_bans(
    state: MatchState, submissions: list[PlayerSubmission]
) -> None:
    for player in (PLAYER_A, PLAYER_B):
        submission = next(
            value for value in submissions if value.player == player
        )
        state.host_banned_branches[player] = list(submission.banned_branches)
        state.host_banned_operator_ids[player] = list(
            submission.banned_operator_ids
        )
    state.ban_complete = True
    state.config.host_banned_branches = {
        player: list(state.host_banned_branches[player])
        for player in (PLAYER_A, PLAYER_B)
    }
    state.config.host_banned_operator_ids = {
        player: list(state.host_banned_operator_ids[player])
        for player in (PLAYER_A, PLAYER_B)
    }
    state.config.bans_finalized = True


def global_bans(operators) -> tuple[list[str], list[str]]:
    branch = sorted({operator.branch for operator in operators.values()})[-1]
    branch_ids = [
        operator.operator_id
        for operator in operators.values()
        if operator.branch == branch
    ]
    individual_ids = [
        operator.operator_id
        for operator in sorted(
            operators.values(),
            key=lambda value: (-value.rarity, value.name),
        )
        if operator.branch != branch
    ][:2]
    return sorted(set(branch_ids + individual_ids)), [branch]


def generate_completed_suite(operators) -> None:
    directory = OUTPUT / "01_已完成BP和拍卖"
    global_ids, global_branches = global_bans(operators)
    config = MatchConfig(
        match_id="DEMO-COMPLETE-001",
        title="联锁对抗完整拍卖测试",
        player_a_name="蓝方测试选手",
        player_b_name="红方测试选手",
        rules=MatchRules(rounds=2, picks_per_round=5),
        global_banned_operator_ids=global_ids,
        global_banned_branches=global_branches,
    )
    submissions = build_submissions(config, operators, rounds=2)
    state = MatchState(config=config, auction_seed=20260727)
    apply_host_bans(state, submissions)
    save_suite_files(directory, config, submissions)
    previous_ids: set[str] = set()
    global_index = 0
    for round_index in (1, 2):
        a = next(
            submission
            for submission in submissions
            if submission.player == PLAYER_A and submission.round_index == round_index
        )
        b = next(
            submission
            for submission in submissions
            if submission.player == PLAYER_B and submission.round_index == round_index
        )
        seed = 20260727 + round_index
        items = build_auction_round(
            config,
            a,
            b,
            operators,
            seed=seed,
            previous_operator_ids=previous_ids,
        )
        state.submissions[f"R{round_index}:A"] = a
        state.submissions[f"R{round_index}:B"] = b
        state.auction_seeds[str(round_index)] = seed
        for item in items:
            if global_index % 6 == 0:
                item.pass_bid(PLAYER_A)
                item.pass_bid(PLAYER_B)
            else:
                winner = PLAYER_A if global_index % 2 == 0 else PLAYER_B
                opponent = PLAYER_B if winner == PLAYER_A else PLAYER_A
                amount = min(
                    config.rules.price_cap,
                    item.starting_price + 2 + global_index % 5,
                )
                item.place_bid(winner, amount, config.rules)
                item.pass_bid(opponent)
            global_index += 1
        state.auction_items.extend(items)
        previous_ids.update(item.operator_id for item in items)

    state.advance()
    for player in (PLAYER_A, PLAYER_B):
        won = [item.operator_id for item in state.auction_items if item.winner == player]
        state.used_operator_ids[player] = won[::2]
        state.perfect_clear[player] = True
    state.notes = "自动生成：BP 与两轮拍卖均已完成，可测试拍卖历史区和结算页。"
    save_state(directory / "已完成比赛存档.bprace", state)
    (directory / "使用说明.txt").write_text(
        "直接在“拍卖”页读取“已完成比赛存档.bprace”。\n"
        "蓝方、红方和流拍区均包含测试数据，结算页也可直接查看。\n",
        encoding="utf-8",
    )


def generate_pending_suite(operators) -> None:
    directory = OUTPUT / "02_已完成BP待拍卖"
    global_ids, global_branches = global_bans(operators)
    config = MatchConfig(
        match_id="DEMO-PENDING-001",
        title="联锁对抗待拍卖测试",
        player_a_name="蓝方测试选手",
        player_b_name="红方测试选手",
        rules=MatchRules(rounds=1, picks_per_round=5),
        global_banned_operator_ids=global_ids,
        global_banned_branches=global_branches,
    )
    submissions = build_submissions(config, operators, rounds=1, candidate_offset=40)
    state = MatchState(config=config)
    apply_host_bans(state, submissions)
    save_suite_files(directory, config, submissions)
    for submission in submissions:
        state.submissions[f"R1:{submission.player}"] = submission
    state.notes = "自动生成：双方 BP 已完成，尚未生成拍卖池。"
    save_state(directory / "待拍卖状态.bprace", state)
    (directory / "使用说明.txt").write_text(
        "在“拍卖”页读取“比赛配置.bpmatch”，随后分别导入：\n"
        "1. A方_第1轮.bpselect\n"
        "2. B方_第1轮.bpselect\n"
        "点击“校验并生成本轮拍卖池”即可开始测试拍卖。\n"
        "“待拍卖状态.bprace”用于检查尚未拍卖时的空状态界面。\n",
        encoding="utf-8",
    )


def main() -> None:
    operators = load_operators(ROOT / "data" / "operators.csv")
    generate_completed_suite(operators)
    generate_pending_suite(operators)
    print(f"测试文件已生成：{OUTPUT}")


if __name__ == "__main__":
    main()
