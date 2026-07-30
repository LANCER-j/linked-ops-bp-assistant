"""下载本地运行所需的可选游戏视觉素材。

游戏素材不会纳入本项目仓库。该脚本根据干员数据表下载头像，并可同时
获取子职业图标字体。素材版权及使用条件以各上游仓库的声明为准。
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import urllib.error
import urllib.request


BASE_URL = (
    "https://raw.githubusercontent.com/"
    "yuanyan3060/ArknightsGameResource/main/avatar/{operator_id}.png"
)
BRANCH_FONT_URL = (
    "https://raw.githubusercontent.com/"
    "tohmatosauce/ak-branch-icons/main/font/600/ak-class-icons-solid.ttf"
)


def download(operator_id: str, output_dir: Path) -> tuple[str, str]:
    target = output_dir / f"{operator_id}.png"
    if target.exists() and target.stat().st_size > 100:
        return operator_id, "cached"
    request = urllib.request.Request(
        BASE_URL.format(operator_id=operator_id),
        headers={"User-Agent": "Arknights-BP-Assistant/0.2"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            content = response.read()
        if len(content) < 100 or not content.startswith(b"\x89PNG"):
            return operator_id, "invalid"
        target.write_bytes(content)
        return operator_id, "downloaded"
    except urllib.error.HTTPError as exc:
        return operator_id, f"http_{exc.code}"
    except (OSError, urllib.error.URLError):
        return operator_id, "failed"


def download_file(url: str, target: Path) -> str:
    """下载一个二进制素材文件，并以临时文件原子替换目标。"""
    if target.exists() and target.stat().st_size > 100:
        return "cached"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Linked-Ops-BP-Assistant/1.0"},
    )
    temporary = target.with_suffix(target.suffix + ".download")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
        if len(content) < 100:
            return "invalid"
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(content)
        temporary.replace(target)
        return "downloaded"
    except urllib.error.HTTPError as exc:
        return f"http_{exc.code}"
    except (OSError, urllib.error.URLError):
        return "failed"
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operators_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument(
        "--branch-font",
        type=Path,
        help="可选：下载子职业图标字体到指定路径",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.operators_csv.open("r", encoding="utf-8-sig", newline="") as file:
        operator_ids = [row["operator_id"] for row in csv.DictReader(file)]

    counts: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(download, operator_id, args.output_dir)
            for operator_id in operator_ids
        ]
        for future in as_completed(futures):
            operator_id, status = future.result()
            counts[status] = counts.get(status, 0) + 1
            if status not in ("cached", "downloaded", "http_404"):
                print(f"{operator_id}: {status}")

    print("头像处理完成：" + "，".join(f"{key}={value}" for key, value in sorted(counts.items())))
    if args.branch_font:
        status = download_file(BRANCH_FONT_URL, args.branch_font)
        print(f"子职业图标字体：{status}（{args.branch_font}）")


if __name__ == "__main__":
    main()
