#!/usr/bin/env python3
"""knowledge_updater.py - VTuber Lore & Dialogue Builder (idea 221).

Crawls character-design, trend/meme, and platform-policy sources, scores and
deduplicates entries by URL hash, appends dated entries to
SECOND-KNOWLEDGE-BRAIN.md, and refreshes the local trend cache
(tools/trend_cache.json) used by sub-dialogue-engine for offline fallback.

Pure-stdlib (urllib + html.parser) so it runs in any production environment
without extra dependencies. Supports dry-run, per-source filtering, and a
configurable timeout. Designed to be safe to re-run: dedup is idempotent.

Usage:
    python tools/knowledge_updater.py                 # live crawl + append + cache
    python tools/knowledge_updater.py --dry-run        # print what would be added
    python tools/knowledge_updater.py --source knowyourmeme
    python tools/knowledge_updater.py --timeout 15 --no-cache
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict, field
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
TREND_CACHE = ROOT / "tools" / "trend_cache.json"
LOG_HEADING = "## Knowledge Update Log"

SOURCES: dict[str, str] = {
    "knowyourmeme": "https://knowyourmeme.com/",
    "twitch_guidelines": "https://safety.twitch.tv/s/article/Community-Guidelines",
    "youtube_policy": "https://www.youtube.com/howyoutubeworks/policies/community-guidelines/",
    "reddit_vtuber": "https://www.reddit.com/r/VirtualYoutubers/",
    "tvtropes": "https://tvtropes.org/",
}

KEYWORDS = [
    "vtuber", "character design", "lore", "world-building", "persona",
    "parasocial", "meme", "trend", "archetype", "dialogue", "community guidelines",
    "safety", "youtube", "twitch",
]

USER_AGENT = "vtuber-lore-dialogue-builder/1.0 (+knowledge-updater)"
DEFAULT_TIMEOUT = 20
HASH_LEN = 12


@dataclass
class Entry:
    """A single crawled knowledge entry."""
    title: str
    summary: str
    url: str
    source: str
    year: int

    def to_log_line(self, run_date: date) -> str:
        h = url_hash(self.url)
        title = self.title or "(untitled)"
        return (
            f"- {run_date.isoformat()} - {title} "
            f"({self.source}, {self.year}) {self.url} <!--h:{h}-->"
        )


@dataclass
class TrendItem:
    """A cached trend for offline use by the dialogue engine."""
    name: str
    url: str
    source: str
    captured: str  # ISO date
    summary: str = ""


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:HASH_LEN]


def existing_hashes(text: str) -> set[str]:
    return set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))


def score_entry(e: Entry) -> float:
    """Higher = more relevant. Recency-weighted keyword match."""
    blob = (e.title + " " + e.summary).lower()
    keyword_hits = sum(1 for k in KEYWORDS if k in blob)
    recency = 1.0 if e.year >= date.today().year - 1 else 0.5
    return keyword_hits * recency


class _TextExtractor(HTMLParser):
    """Stdlib HTML parser that collects visible text and <a> link anchors/urls."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip = 0
        self.text_parts: list[str] = []
        self.links: list[tuple[str, str]] = []  # (anchor_text, href)
        self._title: str = ""
        self._in_title = False
        self._cur_href: str | None = None
        self._cur_anchor: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript", "template"):
            self._skip += 1
            return
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._cur_href = href
                self._cur_anchor = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript", "template") and self._skip > 0:
            self._skip -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._cur_href is not None:
            anchor = " ".join(self._cur_anchor).strip()
            if anchor:
                self.links.append((anchor, self._cur_href))
            self._cur_href = None
            self._cur_anchor = []

    def handle_data(self, data: str) -> None:
        if self._skip > 0:
            return
        if self._in_title:
            self._title += data
        if self._cur_href is not None:
            self._cur_anchor.append(data)
        text = data.strip()
        if text:
            self.text_parts.append(text)

    @property
    def title(self) -> str:
        return self._title.strip()

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)


def fetch(url: str, timeout: int) -> str | None:
    """Fetch a URL and return decoded text, or None on failure."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype and "text" not in ctype and ctype != "":
                return None
            raw = resp.read(2_000_000)  # 2MB cap per page
            return raw.decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"[warn] fetch failed for {url}: {exc}", file=sys.stderr)
        return None


def _absolutize(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href)


def parse_entries(source_name: str, url: str, html: str) -> list[Entry]:
    """Parse HTML into Entry objects using title + top anchor links."""
    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception as exc:  # malformed HTML should not abort the run
        print(f"[warn] parse error for {url}: {exc}", file=sys.stderr)
    base_domain = urllib.parse.urlparse(url).netloc
    page_title = parser.title or source_name
    text = parser.text
    # Year heuristic: look for a 4-digit year 2020-2099 near the top.
    year_match = re.search(r"\b(20[2-9]\d)\b", text[:2000])
    year = int(year_match.group(1)) if year_match else date.today().year

    entries: list[Entry] = []
    # One entry per page (the page itself).
    summary = _summarize(text)
    entries.append(Entry(page_title, summary, url, source_name, year))

    # Plus up to 8 meaningful outbound link entries (trend/lore threads).
    seen: set[str] = {url}
    for anchor, href in parser.links:
        if not anchor or len(anchor) < 4:
            continue
        abs_url = _absolutize(url, href)
        # Keep same-domain or known external targets, drop nav noise.
        target = urllib.parse.urlparse(abs_url)
        if not target.netloc:
            continue
        if abs_url in seen:
            continue
        if any(seg in abs_url.lower() for seg in ("login", "signup", "javascript:", "mailto:", "#")):
            continue
        seen.add(abs_url)
        y_match = re.search(r"\b(20[2-9]\d)\b", anchor)
        e_year = int(y_match.group(1)) if y_match else year
        entries.append(Entry(anchor.strip()[:140], "", abs_url, source_name, e_year))
        if len(entries) >= 9:
            break
    return entries


def _summarize(text: str, limit: int = 240) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:limit]


def crawl(sources: dict[str, str], timeout: int) -> list[Entry]:
    all_entries: list[Entry] = []
    for name, url in sources.items():
        html = fetch(url, timeout)
        if html is None:
            continue
        all_entries.extend(parse_entries(name, url, html))
        time.sleep(0.5)  # polite crawl delay
    return all_entries


def filter_sources(selection: list[str] | None) -> dict[str, str]:
    if not selection:
        return dict(SOURCES)
    return {k: v for k, v in SOURCES.items() if k in selection}


def append_entries(entries: list[Entry], dry_run: bool = False) -> int:
    if not entries:
        return 0
    if not BRAIN.exists():
        print(f"[error] brain file not found: {BRAIN}", file=sys.stderr)
        return 0
    text = BRAIN.read_text(encoding="utf-8")
    seen = existing_hashes(text)
    run_date = date.today()
    to_add: list[Entry] = []
    for e in sorted(entries, key=score_entry, reverse=True):
        if not e.url:
            continue
        h = url_hash(e.url)
        if h in seen:
            continue
        seen.add(h)
        to_add.append(e)
    if not to_add:
        return 0
    lines = [e.to_log_line(run_date) for e in to_add]
    block = "\n".join(lines)
    if dry_run:
        print(f"[dry-run] would append {len(to_add)} entries:\n{block}")
        return len(to_add)
    new_text = _insert_under_log(text, block)
    BRAIN.write_text(new_text, encoding="utf-8")
    return len(to_add)


def _insert_under_log(text: str, block: str) -> str:
    """Insert new log lines right after the LOG_HEADING section start, after any
    existing lines under it, before later top-level sections."""
    idx = text.find(LOG_HEADING)
    if idx == -1:
        # No log heading: append a new section at the end.
        return text.rstrip() + f"\n\n{LOG_HEADING}\n{block}\n"
    # Find end of the log block (next ## heading or end of file).
    after = idx + len(LOG_HEADING)
    next_h = text.find("\n## ", after)
    insert_at = len(text) if next_h == -1 else next_h
    # Insert before the next heading, preserving trailing newline.
    prefix = text[:insert_at].rstrip() + "\n"
    suffix = text[insert_at:]
    if suffix and not suffix.startswith("\n"):
        suffix = "\n" + suffix
    return f"{prefix}{block}\n{suffix}"


def update_trend_cache(entries: list[Entry], dry_run: bool = False) -> int:
    """Write the highest-scoring entries to trend_cache.json for offline fallback."""
    if not entries:
        return 0
    items = [
        TrendItem(
            name=e.title or "(untitled)",
            url=e.url,
            source=e.source,
            captured=datetime.now(timezone.utc).date().isoformat(),
            summary=e.summary,
        )
        for e in sorted(entries, key=score_entry, reverse=True)
        if e.url
    ]
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "items": [asdict(i) for i in items],
    }
    if dry_run:
        print(f"[dry-run] would write {len(items)} items to {TREND_CACHE.name}")
        return len(items)
    TREND_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TREND_CACHE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(items)


def load_trend_cache() -> dict:
    """Public helper used by the dialogue-engine integration / tests."""
    if not TREND_CACHE.exists():
        return {"updated": None, "items": []}
    return json.loads(TREND_CACHE.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Update the second-knowledge-brain for idea 221.")
    ap.add_argument("--dry-run", action="store_true", help="show what would be added; write nothing")
    ap.add_argument("--source", action="append", help="restrict to named source(s); repeatable")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="per-request timeout seconds")
    ap.add_argument("--no-cache", action="store_true", help="skip writing trend_cache.json")
    args = ap.parse_args(argv)

    sources = filter_sources(args.source)
    if args.source and not sources:
        print(f"[error] no matching sources for: {args.source}", file=sys.stderr)
        return 2

    entries = crawl(sources, args.timeout)
    added = append_entries(entries, dry_run=args.dry_run)
    cached = 0 if args.no_cache else update_trend_cache(entries, dry_run=args.dry_run)
    print(f"[221] appended {added} entries to {BRAIN.name}; cached {cached} trends in {TREND_CACHE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
