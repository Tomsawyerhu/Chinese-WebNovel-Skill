#!/usr/bin/env python3
"""Build summaries, tagged excerpts, and imitation indexes for scraped webnovel articles."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "data" / "articles"
OUTPUT_DIR = ROOT / "analysis"


JUNK_PATTERNS = [
    r"^备案号[:：]",
    r"^作者[:：]",
    r"^（全文完）$",
    r"^全文完$",
    r"^——+.*已完结.*——+$",
    r"^\(已完结\)",
    r"^-+完-+$",
    r"^完\s*[-－—]*$",
    r"^拖拽到此处$",
    r"^图片将完成下载$",
    r"^云边的小joly.*$",
    r"^×$",
]

CHAPTER_MARKER_PATTERNS = [
    r"^第?[0-9０-９]+[章回节]?$",
    r"^第[一二三四五六七八九十百千两零〇]+[章回节]$",
    r"^[0-9０-９]+$",
    r"^[0-9０-９]+\s*[、.．]?\s*[一二三四五六七八九十]?$",
    r"^楔子$",
    r"^序章$",
]

KEYWORD_TAGS = [
    ("系统/攻略", [r"系统", r"攻略", r"任务", r"攻略者"]),
    ("弹幕/评论", [r"弹幕", r"评论", r"帖子", r"论坛"]),
    ("真假千金", [r"真千金", r"假千金"]),
    ("古言/宫廷", [r"太子", r"王爷", r"王府", r"宫", r"和离", r"侯府", r"将军"]),
    ("校园", [r"校园", r"学校", r"大学", r"学神", r"宿舍", r"军校"]),
    ("都市婚恋", [r"离婚", r"前夫", r"婚", r"总裁", r"老板"]),
    ("奇幻/异种", [r"恶龙", r"兽人", r"帝国", r"星际", r"魔", r"龙蛋"]),
    ("仙侠/修仙", [r"修仙", r"仙", r"宗门", r"灵根", r"飞升"]),
    ("现实反差", [r"缅北", r"诈骗", r"贫困生", r"自助餐", r"职场"]),
    ("重逢修罗场", [r"重逢", r"回京", r"前男友", r"旧爱", r"再见"]),
    ("身份反差", [r"变成", r"穿成", r"重生", r"失忆", r"冒名", r"身份"]),
    ("危机压身", [r"献祭", r"浸猪笼", r"联姻", r"卖到", r"绑", r"威胁"]),
    ("甜虐关系", [r"喜欢", r"爱", r"吻", r"告白", r"夫君", r"竹马"]),
]


@dataclass
class ArticleProfile:
    article_id: str
    title: str
    file_path: str
    summary: str
    tags: list[str]
    intro_text: str


@dataclass
class Excerpt:
    excerpt_id: str
    article_id: str
    title: str
    file_path: str
    excerpt_type: str
    tags: list[str]
    para_start: int
    para_end: int
    text: str


def normalize_line(line: str) -> str:
    line = line.replace("\u3000", " ").replace("\xa0", " ").strip()
    return re.sub(r"\s+", " ", line)


def is_junk(line: str) -> bool:
    return any(re.search(pattern, line) for pattern in JUNK_PATTERNS)


def is_chapter_marker(line: str) -> bool:
    return any(re.search(pattern, line) for pattern in CHAPTER_MARKER_PATTERNS)


def clean_paragraphs(text: str) -> list[str]:
    paragraphs = [normalize_line(line) for line in text.splitlines()]
    cleaned: list[str] = []
    for para in paragraphs:
        if not para or is_junk(para):
            continue
        cleaned.append(para)
    return cleaned


def detect_chapter_marker_index(paragraphs: list[str]) -> int | None:
    for idx, para in enumerate(paragraphs[:40]):
        if is_chapter_marker(para):
            return idx
    return None


def trim_to_limit(text: str, limit: int = 180) -> str:
    text = re.sub(r"\s+", "", text)
    if len(text) <= limit:
        return text

    sentences = re.split(r"(?<=[。！？!?])", text)
    result = ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(result) + len(sentence) > limit:
            break
        result += sentence

    if result and len(result) >= 60:
        return result
    return text[:limit].rstrip("，,、；; ") + "……"


def build_summary(title: str, paragraphs: list[str]) -> tuple[str, str]:
    marker_idx = detect_chapter_marker_index(paragraphs)
    body_start = marker_idx + 1 if marker_idx is not None else 1

    intro_candidates = paragraphs[1:marker_idx] if marker_idx and marker_idx > 1 else []
    if len(intro_candidates) < 2:
        intro_candidates = paragraphs[1 : min(len(paragraphs), body_start + 6)]

    intro_text = "".join(intro_candidates[:8]).strip()
    summary = trim_to_limit(intro_text or "".join(paragraphs[1:6]))
    if not summary:
        summary = trim_to_limit("".join(paragraphs[:6]))
    return summary, intro_text


def detect_tags(text: str) -> list[str]:
    tags: list[str] = []
    for tag, patterns in KEYWORD_TAGS:
        if any(re.search(pattern, text) for pattern in patterns):
            tags.append(tag)
    if not tags:
        tags.append("其他")
    return tags


def score_dialogue(line: str) -> int:
    score = 0
    if "「" in line and "」" in line:
        score += 3
    if re.search(r"[！？!?]", line):
        score += 2
    if re.search(r"爱|死|滚|嫁|杀|离婚|不要|别|会|敢|疯|喜欢", line):
        score += 2
    if 12 <= len(line) <= 80:
        score += 1
    return score


def find_character_intro(paragraphs: list[str]) -> tuple[int, int]:
    for idx in range(1, min(len(paragraphs), 40)):
        para = paragraphs[idx]
        if is_chapter_marker(para):
            continue
        if re.match(r"^(我|我是|我今年|成婚|最爱我那年|父亲要把我|我在|我把自己|十六岁那年)", para):
            return idx, idx
    return 1, 1


def choose_opening_excerpt(paragraphs: list[str]) -> tuple[int, int]:
    marker_idx = detect_chapter_marker_index(paragraphs)
    end_idx = marker_idx - 1 if marker_idx and marker_idx > 2 else min(5, len(paragraphs) - 1)
    start_idx = 1
    while start_idx < len(paragraphs) and is_chapter_marker(paragraphs[start_idx]):
        start_idx += 1
    end_idx = max(start_idx, min(end_idx, start_idx + 4))
    return start_idx, end_idx


def choose_dialogue_excerpt(paragraphs: list[str]) -> tuple[int, int] | None:
    best: tuple[int, int] | None = None
    best_score = 0
    for idx, para in enumerate(paragraphs[:120]):
        score = score_dialogue(para)
        if score > best_score:
            best = (idx, idx)
            best_score = score
    return best if best_score >= 4 else None


def choose_ending_excerpt(paragraphs: list[str]) -> tuple[int, int]:
    if len(paragraphs) <= 3:
        return 0, len(paragraphs) - 1
    start = max(0, len(paragraphs) - 3)
    return start, len(paragraphs) - 1


def join_excerpt(paragraphs: list[str], start: int, end: int) -> str:
    return "\n".join(paragraphs[start : end + 1]).strip()


def detect_excerpt_tags(excerpt_type: str, text: str, article_tags: list[str]) -> list[str]:
    tags = list(article_tags)
    tags.append(excerpt_type)
    if re.search(r"离婚|和离|分手|退婚", text):
        tags.append("关系破裂")
    if re.search(r"系统|弹幕|攻略|任务", text):
        tags.append("信息外挂")
    if re.search(r"危机|威胁|炸|献祭|联姻|缅北|浸猪笼", text):
        tags.append("危机感")
    if re.search(r"笑|可爱|扭扭车|病情", text):
        tags.append("轻喜反差")
    if re.search(r"爱|喜欢|夫君|竹马|重逢", text):
        tags.append("情感拉扯")
    if re.search(r"我|主角|公主|真千金|兽人|学神", text):
        tags.append("人设亮相")
    deduped: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            deduped.append(tag)
    return deduped


def build_excerpts(article_id: str, title: str, file_path: str, paragraphs: list[str], article_tags: list[str]) -> list[Excerpt]:
    excerpts: list[Excerpt] = []

    opening_start, opening_end = choose_opening_excerpt(paragraphs)
    excerpts.append(
        Excerpt(
            excerpt_id=f"{article_id}-opening",
            article_id=article_id,
            title=title,
            file_path=file_path,
            excerpt_type="开头钩子",
            tags=detect_excerpt_tags("开头钩子", join_excerpt(paragraphs, opening_start, opening_end), article_tags),
            para_start=opening_start,
            para_end=opening_end,
            text=join_excerpt(paragraphs, opening_start, opening_end),
        )
    )

    intro_start, intro_end = find_character_intro(paragraphs)
    excerpts.append(
        Excerpt(
            excerpt_id=f"{article_id}-intro",
            article_id=article_id,
            title=title,
            file_path=file_path,
            excerpt_type="主角亮相",
            tags=detect_excerpt_tags("主角亮相", join_excerpt(paragraphs, intro_start, intro_end), article_tags),
            para_start=intro_start,
            para_end=intro_end,
            text=join_excerpt(paragraphs, intro_start, intro_end),
        )
    )

    dialogue_span = choose_dialogue_excerpt(paragraphs)
    if dialogue_span is not None:
        start, end = dialogue_span
        excerpts.append(
            Excerpt(
                excerpt_id=f"{article_id}-dialogue",
                article_id=article_id,
                title=title,
                file_path=file_path,
                excerpt_type="高张力对白",
                tags=detect_excerpt_tags("高张力对白", join_excerpt(paragraphs, start, end), article_tags),
                para_start=start,
                para_end=end,
                text=join_excerpt(paragraphs, start, end),
            )
        )

    ending_start, ending_end = choose_ending_excerpt(paragraphs)
    excerpts.append(
        Excerpt(
            excerpt_id=f"{article_id}-ending",
            article_id=article_id,
            title=title,
            file_path=file_path,
            excerpt_type="结尾余韵",
            tags=detect_excerpt_tags("结尾余韵", join_excerpt(paragraphs, ending_start, ending_end), article_tags),
            para_start=ending_start,
            para_end=ending_end,
            text=join_excerpt(paragraphs, ending_start, ending_end),
        )
    )

    return excerpts


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_article_profiles_csv(path: Path, profiles: list[ArticleProfile]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["article_id", "title", "file_path", "summary_le_200", "tags", "intro_text"])
        for profile in profiles:
            writer.writerow(
                [
                    profile.article_id,
                    profile.title,
                    profile.file_path,
                    profile.summary,
                    "|".join(profile.tags),
                    profile.intro_text,
                ]
            )


def write_excerpt_csv(path: Path, excerpts: list[Excerpt]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["excerpt_id", "article_id", "title", "file_path", "excerpt_type", "tags", "para_start", "para_end", "text"]
        )
        for excerpt in excerpts:
            writer.writerow(
                [
                    excerpt.excerpt_id,
                    excerpt.article_id,
                    excerpt.title,
                    excerpt.file_path,
                    excerpt.excerpt_type,
                    "|".join(excerpt.tags),
                    excerpt.para_start,
                    excerpt.para_end,
                    excerpt.text,
                ]
            )


def build_index_markdown(profiles: list[ArticleProfile], excerpts: list[Excerpt]) -> str:
    grouped: dict[str, dict[str, list[Excerpt]]] = defaultdict(lambda: defaultdict(list))
    for excerpt in excerpts:
        excerpt_type = excerpt.excerpt_type
        thematic_tags = [tag for tag in excerpt.tags if tag not in {excerpt_type, "人设亮相"}]
        category = thematic_tags[0] if thematic_tags else "其他"
        grouped[excerpt_type][category].append(excerpt)

    lines: list[str] = []
    lines.append("# 模仿索引\n")
    lines.append("这份索引按“摘录类型 -> 主题标签”整理，方便在写作时按结构模仿与回查原文。\n")
    lines.append("## 文章摘要索引\n")
    for profile in profiles:
        lines.append(
            f"- `{profile.article_id}` 《{profile.title}》 | 标签：{' / '.join(profile.tags)} | 摘要：{profile.summary} | 原文：`{profile.file_path}`"
        )

    for excerpt_type in ["开头钩子", "主角亮相", "高张力对白", "结尾余韵"]:
        if excerpt_type not in grouped:
            continue
        lines.append(f"\n## {excerpt_type}\n")
        for category, items in sorted(grouped[excerpt_type].items(), key=lambda pair: (-len(pair[1]), pair[0])):
            lines.append(f"### {category}\n")
            for excerpt in items:
                lines.append(
                    f"- `{excerpt.excerpt_id}` 《{excerpt.title}》 | 标签：{' / '.join(excerpt.tags)} | 段落：{excerpt.para_start}-{excerpt.para_end} | 原文：`{excerpt.file_path}`"
                )
                lines.append("")
                lines.append(f"> {excerpt.text.replace(chr(10), chr(10) + '> ')}")
                lines.append("")

    return "\n".join(lines).strip() + "\n"


def build_stats(profiles: list[ArticleProfile], excerpts: list[Excerpt]) -> dict:
    tag_counter = Counter(tag for profile in profiles for tag in profile.tags)
    excerpt_type_counter = Counter(excerpt.excerpt_type for excerpt in excerpts)
    return {
        "article_count": len(profiles),
        "excerpt_count": len(excerpts),
        "top_article_tags": tag_counter.most_common(20),
        "excerpt_type_counts": dict(excerpt_type_counter),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    profiles: list[ArticleProfile] = []
    excerpts: list[Excerpt] = []

    article_files = sorted(ARTICLES_DIR.glob("*.txt"))
    for index, path in enumerate(article_files, start=1):
        article_id = f"A{index:03d}"
        raw_text = path.read_text(encoding="utf-8")
        paragraphs = clean_paragraphs(raw_text)
        if not paragraphs:
            continue

        title = paragraphs[0]
        summary, intro_text = build_summary(title, paragraphs)
        tags = detect_tags(f"{title}\n{summary}\n{intro_text}")

        profile = ArticleProfile(
            article_id=article_id,
            title=title,
            file_path=str(path.relative_to(ROOT)),
            summary=summary,
            tags=tags,
            intro_text=intro_text,
        )
        profiles.append(profile)
        excerpts.extend(build_excerpts(article_id, title, profile.file_path, paragraphs, tags))

    write_article_profiles_csv(OUTPUT_DIR / "article_profiles.csv", profiles)
    write_jsonl(OUTPUT_DIR / "article_profiles.jsonl", [profile.__dict__ for profile in profiles])
    write_excerpt_csv(OUTPUT_DIR / "excerpts.csv", excerpts)
    write_jsonl(OUTPUT_DIR / "excerpts.jsonl", [excerpt.__dict__ for excerpt in excerpts])
    (OUTPUT_DIR / "imitation_index.md").write_text(build_index_markdown(profiles, excerpts), encoding="utf-8")
    (OUTPUT_DIR / "stats.json").write_text(
        json.dumps(build_stats(profiles, excerpts), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
