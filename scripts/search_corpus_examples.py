#!/usr/bin/env python3
"""Search generated corpus profiles and excerpts by tag, type, and keyword."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = ROOT / "analysis"
SUGGESTED_KEYWORDS = [
    "弹幕",
    "系统",
    "攻略",
    "真假千金",
    "重生",
    "穿书",
    "联姻",
    "和离",
    "离婚",
    "前夫",
    "校园",
    "学神",
    "竹马",
    "重逢",
    "恶龙",
    "修仙",
    "河神",
    "末世",
    "缅北",
    "豪门",
]
STRUCTURAL_TAGS = {
    "开头钩子",
    "主角亮相",
    "高张力对白",
    "结尾余韵",
    "人设亮相",
    "情感拉扯",
    "轻喜反差",
    "信息外挂",
    "关系破裂",
    "危机感",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检索网文语料范例索引。")
    parser.add_argument("--tag", help="按标签检索，例如：弹幕/评论、古言/宫廷、开头钩子")
    parser.add_argument("--type", help="按摘录类型检索，例如：开头钩子、高张力对白、结尾余韵")
    parser.add_argument("--keyword", help="按关键词检索标题、摘要或摘录文本")
    parser.add_argument("--limit", type=int, default=10, help="最多返回多少条，默认 10")
    parser.add_argument("--list-tags", action="store_true", help="列出当前语料库中可用的标签")
    parser.add_argument("--list-types", action="store_true", help="列出当前语料库中可用的摘录类型")
    parser.add_argument(
        "--list-keyword-examples",
        action="store_true",
        help="列出推荐尝试的关键词示例",
    )
    return parser.parse_args()


def matches(value: str, target: str | None) -> bool:
    if not target:
        return True
    return target in value


def collect_tags(rows: list[dict[str, str]], field: str = "tags") -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        for tag in row[field].split("|"):
            tag = tag.strip()
            if tag:
                counter[tag] += 1
    return counter


def print_available_items(profiles: list[dict[str, str]], excerpts: list[dict[str, str]], args: argparse.Namespace) -> int:
    printed = False

    if args.list_tags:
        profile_tags = collect_tags(profiles)
        excerpt_tags = collect_tags(excerpts)
        merged: Counter[str] = Counter()
        merged.update(profile_tags)
        merged.update(excerpt_tags)
        thematic = [(tag, count) for tag, count in merged.items() if tag not in STRUCTURAL_TAGS]
        structural = [(tag, count) for tag, count in merged.items() if tag in STRUCTURAL_TAGS]
        print("可用题材/主题标签：")
        for tag, count in sorted(thematic, key=lambda item: (-item[1], item[0])):
            print(f"- {tag} ({count})")
        print()
        print("可用结构标签：")
        for tag, count in sorted(structural, key=lambda item: (-item[1], item[0])):
            print(f"- {tag} ({count})")
        printed = True

    if args.list_types:
        type_counter = Counter(row["excerpt_type"] for row in excerpts)
        if printed:
            print()
        print("可用摘录类型：")
        for excerpt_type, count in sorted(type_counter.items(), key=lambda item: (-item[1], item[0])):
            print(f"- {excerpt_type} ({count})")
        printed = True

    if args.list_keyword_examples:
        if printed:
            print()
        print("推荐关键词示例：")
        for keyword in SUGGESTED_KEYWORDS:
            print(f"- {keyword}")
        print()
        print("说明：")
        print("- `--tag` 和 `--type` 是固定集合，适合精确筛选。")
        print("- `--keyword` 是全文模糊匹配，不是固定列表，可以自由输入人物、题材、事件、设定词。")
        printed = True

    return 0 if printed else -1


def main() -> int:
    args = parse_args()
    profiles = load_csv(ANALYSIS_DIR / "article_profiles.csv")
    excerpts = load_csv(ANALYSIS_DIR / "excerpts.csv")

    listed = print_available_items(profiles, excerpts, args)
    if listed == 0:
        return 0

    results: list[tuple[str, dict[str, str]]] = []

    for row in profiles:
        haystack = "\n".join([row["title"], row["summary_le_200"], row["tags"]])
        if not matches(row["tags"], args.tag):
            continue
        if args.keyword and args.keyword not in haystack:
            continue
        results.append(("article", row))

    for row in excerpts:
        haystack = "\n".join([row["title"], row["tags"], row["text"], row["excerpt_type"]])
        if not matches(row["tags"], args.tag):
            continue
        if not matches(row["excerpt_type"], args.type):
            continue
        if args.keyword and args.keyword not in haystack:
            continue
        results.append(("excerpt", row))

    results = results[: args.limit]
    for kind, row in results:
        if kind == "article":
            print(f"[ARTICLE] {row['article_id']} 《{row['title']}》")
            print(f"标签: {row['tags']}")
            print(f"路径: {row['file_path']}")
            print(f"摘要: {row['summary_le_200']}")
            print()
        else:
            print(f"[EXCERPT] {row['excerpt_id']} 《{row['title']}》")
            print(f"类型: {row['excerpt_type']}")
            print(f"标签: {row['tags']}")
            print(f"路径: {row['file_path']} | 段落: {row['para_start']}-{row['para_end']}")
            print(row["text"])
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
