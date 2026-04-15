#!/usr/bin/env python3
"""Scrape yanxuan recent posts and save metadata plus article text under data/."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from fetch_content_raw import extract_matches, fetch_html_http, html_to_text, resolve_matches


@dataclass
class RecentPost:
    title: str
    published_at: str
    url: str


class RecentPostParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.posts: list[RecentPost] = []
        self._current: dict[str, str] | None = None
        self._depth = 0
        self._inside_post_title = False
        self._capture_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()

        if tag == "div" and "recent-post-item" in classes:
            self._current = {"title": "", "published_at": "", "url": ""}
            self._depth = 1
            self._inside_post_title = False
            self._capture_title = False
            self._title_parts = []
            return

        if not self._current:
            return

        if tag == "div":
            self._depth += 1

        if tag == "h2" and "post-title" in classes:
            self._inside_post_title = True
            return

        if tag == "a" and self._inside_post_title:
            href = attrs_dict.get("href") or ""
            self._current["url"] = urljoin(self.base_url, href)
            self._capture_title = True
            self._title_parts = []
            return

        if tag == "time":
            title = (attrs_dict.get("title") or "").strip()
            datetime_value = (attrs_dict.get("datetime") or "").strip()
            self._current["published_at"] = title or datetime_value

    def handle_endtag(self, tag: str) -> None:
        if not self._current:
            return

        if tag == "a" and self._capture_title:
            self._current["title"] = "".join(self._title_parts).strip()
            self._capture_title = False
            return

        if tag == "h2" and self._inside_post_title:
            self._inside_post_title = False
            return

        if tag == "div":
            self._depth -= 1
            if self._depth == 0:
                title = self._current["title"].strip()
                published_at = self._current["published_at"].strip()
                url = self._current["url"].strip()
                if title and published_at and url:
                    self.posts.append(
                        RecentPost(title=title, published_at=published_at, url=url)
                    )
                self._current = None
                self._inside_post_title = False
                self._capture_title = False
                self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)


def parse_recent_posts(html: str, base_url: str) -> list[RecentPost]:
    parser = RecentPostParser(base_url=base_url)
    parser.feed(html)
    parser.close()

    deduped: list[RecentPost] = []
    seen: set[str] = set()
    for post in parser.posts:
        if post.url in seen:
            continue
        seen.add(post.url)
        deduped.append(post)
    return deduped


def is_article_url(url: str) -> bool:
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if not parts:
        return False
    return parts[0] in {"yanxuan", "novel"}


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" .")
    return cleaned[:120] or "untitled"


def fetch_article_text(url: str, timeout: float) -> str:
    html = fetch_html_http(url, timeout=timeout)
    matches = resolve_matches(extract_matches(html, target_class="content_raw"))
    if not matches:
        raise ValueError('没有找到 class="content_raw" 的正文块')

    text_parts = [html_to_text(match).strip() for match in matches if match.strip()]
    text = "\n\n".join(part for part in text_parts if part)
    if not text:
        raise ValueError("正文块存在，但解码后为空")
    return text


def write_metadata_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_metadata_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "id",
        "title",
        "published_at",
        "url",
        "file_path",
        "status",
        "char_count",
        "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="抓取 yanxuan 首页 recent-post-item 列表中的文章正文。"
    )
    parser.add_argument(
        "--base-url",
        default="https://www.yanxuan.org/",
        help="站点首页 URL，默认 https://www.yanxuan.org/",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="输出目录，默认 data",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=40.0,
        help="单次请求超时时间，默认 40 秒",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="每篇文章抓取后的延迟秒数，默认 0.2",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="只抓取前 N 篇，默认抓全部",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    articles_dir = output_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    homepage_html = fetch_html_http(args.base_url, timeout=args.timeout)
    posts = [
        post
        for post in parse_recent_posts(homepage_html, base_url=args.base_url)
        if is_article_url(post.url)
    ]
    if args.limit is not None:
        posts = posts[: args.limit]

    if not posts:
        print("没有在首页找到 recent-post-item。", file=sys.stderr)
        return 1

    metadata_rows: list[dict[str, object]] = []
    total = len(posts)

    for index, post in enumerate(posts, start=1):
        file_name = f"{index:04d}-{sanitize_filename(post.title)}.txt"
        relative_path = Path("articles") / file_name
        article_path = output_dir / relative_path
        status = "ok"
        error = ""
        char_count = 0

        try:
            text = fetch_article_text(post.url, timeout=args.timeout)
            article_path.write_text(text, encoding="utf-8")
            char_count = len(text)
            print(f"[{index}/{total}] saved {post.title}")
        except Exception as exc:
            status = "error"
            error = str(exc)
            print(f"[{index}/{total}] failed {post.title}: {exc}", file=sys.stderr)

        metadata_rows.append(
            {
                "id": index,
                "title": post.title,
                "published_at": post.published_at,
                "url": post.url,
                "file_path": str(relative_path),
                "status": status,
                "char_count": char_count,
                "error": error,
            }
        )

        if args.delay > 0:
            time.sleep(args.delay)

    write_metadata_jsonl(output_dir / "metadata.jsonl", metadata_rows)
    write_metadata_csv(output_dir / "metadata.csv", metadata_rows)

    success_count = sum(1 for row in metadata_rows if row["status"] == "ok")
    print(
        f"finished: total={total}, success={success_count}, failed={total - success_count}"
    )
    return 0 if success_count == total else 2


if __name__ == "__main__":
    raise SystemExit(main())
