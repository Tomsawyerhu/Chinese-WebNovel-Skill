#!/usr/bin/env python3
"""Fetch and extract the content of elements with a target class from a URL."""

from __future__ import annotations

import argparse
import base64
import binascii
import re
import sys
import time
import urllib.error
import urllib.request
import zlib
from html.parser import HTMLParser
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def render_starttag(tag: str, attrs: list[tuple[str, str | None]]) -> str:
    parts = [tag]
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            escaped = value.replace('"', "&quot;")
            parts.append(f'{key}="{escaped}"')
    return "<" + " ".join(parts) + ">"


def render_startendtag(tag: str, attrs: list[tuple[str, str | None]]) -> str:
    parts = [tag]
    for key, value in attrs:
        if value is None:
            parts.append(key)
        else:
            escaped = value.replace('"', "&quot;")
            parts.append(f'{key}="{escaped}"')
    return "<" + " ".join(parts) + " />"


class ContentRawHTMLExtractor(HTMLParser):
    def __init__(self, target_class: str) -> None:
        super().__init__(convert_charrefs=True)
        self.target_class = target_class
        self.matches: list[str] = []
        self._capturing = False
        self._depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._capturing:
            self._chunks.append(render_starttag(tag, attrs))
            self._depth += 1
            return

        class_value = next((value for key, value in attrs if key == "class"), None)
        classes = class_value.split() if class_value else []
        if self.target_class in classes:
            self._capturing = True
            self._depth = 1
            self._chunks = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._capturing:
            self._chunks.append(render_startendtag(tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        if not self._capturing:
            return

        if self._depth > 1:
            self._chunks.append(f"</{tag}>")
            self._depth -= 1
            return

        self.matches.append("".join(self._chunks).strip())
        self._capturing = False
        self._depth = 0
        self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._capturing:
            self._chunks.append(data)

    def handle_comment(self, data: str) -> None:
        if self._capturing:
            self._chunks.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        if self._capturing:
            self._chunks.append(f"<!{decl}>")

    def unknown_decl(self, data: str) -> None:
        if self._capturing:
            self._chunks.append(f"<![{data}]>")


class TextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        text = "".join(self.parts)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def html_to_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def decode_response(raw: bytes, charset_hint: str | None = None) -> str:
    tried: list[str] = []
    for encoding in [charset_hint, "utf-8", "gb18030", "big5"]:
        if not encoding or encoding in tried:
            continue
        tried.append(encoding)
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        raise ValueError("URL 缺少协议或域名，例如 https://example.com/path")

    netloc = parts.netloc.encode("idna").decode("ascii")
    path = quote(parts.path or "/", safe="/%:@+~!$,;=-._")
    query = urlencode(parse_qsl(parts.query, keep_blank_values=True), doseq=True)
    fragment = quote(parts.fragment, safe="")
    return urlunsplit((parts.scheme, netloc, path, query, fragment))


def fetch_html_http(url: str, timeout: float) -> str:
    normalized_url = normalize_url(url)
    request = urllib.request.Request(
        normalized_url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                charset = response.headers.get_content_charset()
                return decode_response(raw, charset)
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))

    if last_error:
        raise last_error
    raise RuntimeError("未能获取页面内容")


def build_css_selector(class_name: str) -> str:
    classes = [part.strip() for part in class_name.split() if part.strip()]
    if not classes:
        raise ValueError("class-name 不能为空")
    return "".join(f".{name}" for name in classes)


def create_chrome_driver(show_browser: bool, timeout: float) -> webdriver.Chrome:
    options = ChromeOptions()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.page_load_strategy = "eager"
    if not show_browser:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--window-size=1440,2200")
    options.add_argument(
        "--user-agent="
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.set_page_load_timeout(timeout)
    return driver


def fetch_html_browser(
    url: str,
    class_name: str,
    timeout: float,
    show_browser: bool,
) -> list[str]:
    normalized_url = normalize_url(url)
    selector = build_css_selector(class_name)
    driver = create_chrome_driver(show_browser=show_browser, timeout=timeout)

    try:
        try:
            driver.get(normalized_url)
        except TimeoutException:
            # Some sites keep loading secondary resources for a long time.
            # Continue and inspect the current DOM instead of failing early.
            pass
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        time.sleep(1)
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        return [element.get_attribute("innerHTML").strip() for element in elements]
    finally:
        driver.quit()


def decode_compressed_story(fragment: str) -> str | None:
    match = re.search(
        r'<script[^>]+id=["\']compressed-story["\'][^>]*>(.*?)</script>',
        fragment,
        re.S,
    )
    if not match:
        return None

    encoded = match.group(1).strip()
    if not encoded:
        return None

    try:
        compressed = base64.b64decode(encoded)
        decoded = zlib.decompress(compressed)
    except (binascii.Error, zlib.error):
        return None

    return decoded.decode("utf-8", errors="replace").strip()


def resolve_matches(matches: list[str]) -> list[str]:
    resolved: list[str] = []
    for match in matches:
        decoded = decode_compressed_story(match)
        resolved.append(decoded if decoded is not None else match)
    return resolved


def extract_matches(html: str, target_class: str) -> list[str]:
    parser = ContentRawHTMLExtractor(target_class=target_class)
    parser.feed(html)
    parser.close()
    return parser.matches


def build_output(matches: list[str], output_html: bool) -> str:
    if output_html:
        return "\n\n".join(match for match in matches if match)
    return "\n\n".join(html_to_text(match) for match in matches if match)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="抓取指定 URL 中 class=content_raw 的内容。默认优先用 HTTP 抓取并自动解压正文。"
    )
    parser.add_argument("url", help="要抓取的页面 URL")
    parser.add_argument(
        "--class-name",
        default="content_raw",
        help="目标 class 名，默认是 content_raw",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="输出原始 HTML，而不是纯文本",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出文件路径；不传则直接打印到终端",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="超时时间，单位秒，默认 30",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="强制使用浏览器模式抓取",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="显示浏览器窗口，默认无头模式运行",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.browser:
            matches = fetch_html_browser(
                args.url,
                class_name=args.class_name,
                timeout=args.timeout,
                show_browser=args.show_browser,
            )
            matches = resolve_matches(matches)
        else:
            html = fetch_html_http(args.url, timeout=args.timeout)
            matches = extract_matches(html, target_class=args.class_name)
            matches = resolve_matches(matches)
    except ValueError as exc:
        print(f"URL 无效: {exc}", file=sys.stderr)
        return 1
    except TimeoutException:
        print("浏览器等待页面或目标元素超时。", file=sys.stderr)
        return 1
    except WebDriverException as exc:
        print(f"浏览器启动或执行失败: {exc}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"请求失败: {exc}", file=sys.stderr)
        return 1

    if not matches:
        print(
            f'没有找到 class="{args.class_name}" 的内容。'
            " 如果站点对直连有限制，可以尝试加 --browser。",
            file=sys.stderr,
        )
        return 2

    output = build_output(matches, output_html=args.html)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
    else:
        try:
            print(output)
        except BrokenPipeError:
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
