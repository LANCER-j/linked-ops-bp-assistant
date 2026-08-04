from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .core import (
    MatchConfig,
    MatchState,
    Operator,
    PlayerSubmission,
    config_from_dict,
    dataclass_to_dict,
    make_envelope,
    state_from_dict,
    submission_from_dict,
    verify_envelope,
)


def load_operators(path: Path) -> dict[str, Operator]:
    operators: dict[str, Operator] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            operator = Operator(
                operator_id=row["operator_id"].strip(),
                name=row["name"].strip(),
                rarity=int(row["rarity"]),
                profession=row["profession"].strip(),
                branch=row["branch"].strip(),
                branch_id=row.get("branch_id", "").strip(),
            )
            operators[operator.operator_id] = operator
    return operators


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_config(path: Path, config: MatchConfig) -> None:
    save_json(path, make_envelope("match_config", dataclass_to_dict(config)))


def load_config(path: Path) -> MatchConfig:
    payload = verify_envelope(load_json(path), "match_config")
    return config_from_dict(payload)


def save_submission(path: Path, submission: PlayerSubmission) -> None:
    save_json(path, make_envelope("player_submission", dataclass_to_dict(submission)))


def load_submission(path: Path) -> PlayerSubmission:
    payload = verify_envelope(load_json(path), "player_submission")
    return submission_from_dict(payload)


def save_state(path: Path, state: MatchState) -> None:
    save_json(path, make_envelope("match_state", dataclass_to_dict(state)))


def load_state(path: Path) -> MatchState:
    payload = verify_envelope(load_json(path), "match_state")
    return state_from_dict(payload)


def export_results_csv(
    path: Path,
    state: MatchState,
    operators: dict[str, Operator],
) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["轮次", "干员", "星级", "职业", "分支", "提名方", "归属", "成交价", "是否上场"]
        )
        for item in state.auction_items:
            operator = operators[item.operator_id]
            used = item.winner and item.operator_id in state.used_operator_ids[item.winner]
            writer.writerow(
                [
                    item.round_index,
                    operator.name,
                    operator.rarity,
                    operator.profession,
                    operator.branch,
                    "/".join(item.nominated_by),
                    item.winner or "流拍",
                    item.final_price if item.final_price is not None else "",
                    "是" if used else "否",
                ]
            )
        if state.auction_complete:
            result = state.result()
            writer.writerow([])
            writer.writerow(
                [
                    "选手",
                    "使用成本",
                    "未使用原价",
                    "未使用折算",
                    "修正前总消耗",
                    "分数修正",
                    "最终总消耗",
                    "完美通关",
                ]
            )
            for player in ("A", "B"):
                score = result[player]
                writer.writerow(
                    [
                        player,
                        score["used_cost"],
                        score["bench_full_cost"],
                        score["bench_weighted_cost"],
                        score["base_total"],
                        score["adjustment"],
                        score["total"],
                        "是" if state.perfect_clear[player] else "否",
                    ]
                )
            writer.writerow(["胜者", result["winner"] or "无/平局", result["reason"]])


def operator_values(operators: Iterable[Operator], attribute: str) -> list[str]:
    return sorted({str(getattr(operator, attribute)) for operator in operators})
