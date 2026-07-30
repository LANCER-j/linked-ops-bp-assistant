"""从公开游戏数据生成软件使用的精简干员表。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROFESSIONS = {
    "PIONEER": "先锋",
    "WARRIOR": "近卫",
    "SNIPER": "狙击",
    "TANK": "重装",
    "MEDIC": "医疗",
    "SUPPORT": "辅助",
    "CASTER": "术师",
    "SPECIAL": "特种",
}


def build(character_path: Path, uniequip_path: Path, output_path: Path) -> int:
    characters = json.loads(character_path.read_text(encoding="utf-8"))
    uniequip = json.loads(uniequip_path.read_text(encoding="utf-8"))
    branches = {
        key: value["subProfessionName"]
        for key, value in uniequip["subProfDict"].items()
    }

    rows = []
    for operator_id, data in characters.items():
        profession_id = data.get("profession")
        if profession_id not in PROFESSIONS or data.get("isNotObtainable"):
            continue
        rarity_text = data.get("rarity", "")
        if not rarity_text.startswith("TIER_"):
            continue
        branch_id = data.get("subProfessionId", "")
        rows.append(
            {
                "operator_id": operator_id,
                "name": data["name"],
                "rarity": int(rarity_text.removeprefix("TIER_")),
                "profession": PROFESSIONS[profession_id],
                "branch": branches.get(branch_id, branch_id),
                "branch_id": branch_id,
            }
        )
    rows.sort(key=lambda row: (-row["rarity"], row["profession"], row["name"]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["operator_id", "name", "rarity", "profession", "branch", "branch_id"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("character_table", type=Path)
    parser.add_argument("uniequip_table", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    count = build(args.character_table, args.uniequip_table, args.output)
    print(f"已生成 {count} 名干员：{args.output}")


if __name__ == "__main__":
    main()

