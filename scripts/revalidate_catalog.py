#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Revalidate the whole skill catalog against the live world (L5).

Where scripts/lint_references.py gates a single PR, this script sweeps *all*
skills periodically and reports rot that appeared after merge: actors that got
deprecated, made private or deleted, author pages that vanished, external links
that died.

Extraction and classification are reused from lint_references (repo-path /
actor-id / store-url / apify-url), so both tools always agree on what a
"reference" is. Only the checks and the reporting differ:

  - every finding is a WARNING; the exit code is always 0
  - the output is a report (machine JSON + markdown for a GitHub issue),
    never a gate

Checks
  actor-id / store-url  existence, isPublic, isDeprecated via the public,
                        unauthenticated Apify API (lint_references.fetch_actor_status)
  author_url            liveness of the frontmatter author page
  external-url          liveness of non-Apify links used in prose
                        (URLs that only appear inside fenced code blocks are
                        sample payloads, not links — they are not checked)

Placeholder-looking URLs (example.com, .../idNUMBER, https://…) are skipped, and
anything the network refuses to answer for (403/429/5xx/timeouts) is reported as
"unverifiable", not as a finding — a weekly report must not cry wolf.

Authors are attributed from the `author_url` frontmatter field. Handles are
rendered in backticks by default; --mention-authors switches to live @mentions
(only ever use that on a repo where pinging those people is intended).

Usage:
  uv run scripts/revalidate_catalog.py                        # full catalog, markdown to stdout
  uv run scripts/revalidate_catalog.py --json-out report.json --markdown-out report.md
  uv run scripts/revalidate_catalog.py skills/apify-ecommerce  # subset, for debugging
  uv run scripts/revalidate_catalog.py --skip-external         # actors only (fast)
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint_references as lint  # noqa: E402  (path bootstrap above)

ROOT = lint.ROOT

# Marker kept in the issue body so a run can recognise (and update) the issue a
# previous run opened, even if the tracking label was removed by hand.
REPORT_MARKER = "<!-- revalidate-catalog-report -->"

# Network defaults. All three are overridable from the CLI — a scheduled run on
# a slow runner may need a longer timeout, a rate-limited API a longer interval.
DEFAULT_TIMEOUT = 10        # seconds per HTTP request
DEFAULT_RETRIES = 2         # extra attempts on transient failures
DEFAULT_WORKERS = 6         # parallel in-flight requests
DEFAULT_MIN_INTERVAL = 0.2  # seconds between two requests to the same host
USER_AGENT = "apify-awesome-skills/revalidate_catalog"

FRONTMATTER_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")
GITHUB_HANDLE_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")

# Documentation examples that must never be fetched: they are illustrations of a
# URL shape, not links. Everything below is calibrated against the catalog.
PLACEHOLDER_HOSTS = {
    "acme.com", "apifyclone.com", "domain", "example.com", "example.net",
    "example.org", "localhost", "mydomain.com", "test.com", "www.acme.com",
    "www.example.com", "yourdomain.com",
}
PLACEHOLDER_UPPER_RE = re.compile(
    r"(?:YOUR_[A-Z_]+|[A-Z_]*SLUG\b|[A-Z_]*NUMBER\b|PLACEHOLDER|XXXX)"
)
PLACEHOLDER_SEGMENTS = {
    "app-name", "company-name", "handle", "keyword", "place_id", "some-handle",
    "subreddit", "username", "yourcompany", "yourhandle",
}

# Finding kinds, in report order. Value = human-readable section heading.
FINDING_KINDS = {
    "actor-missing": "Actors that no longer exist on Apify Store",
    "actor-private": "Actors that are no longer public",
    "actor-deprecated": "Deprecated actors",
    "author-url-dead": "Dead author URLs",
    "external-url-dead": "Dead external links",
}


# --- catalog model --------------------------------------------------------


class Skill:
    """One skill directory plus everything the checks need from it."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.author = ""
        self.author_url = ""
        self.files: list[Path] = []
        # value -> sorted list of "skills/<name>/FILE.md:<line>" locations
        self.actor_ids: dict[str, list[str]] = {}
        self.external_urls: dict[str, list[str]] = {}

    @property
    def author_handle(self) -> str:
        return github_handle(self.author_url)


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    """Top-level scalar fields of the SKILL.md YAML frontmatter.

    Deliberately not a YAML parser: only flat `key: value` lines of the leading
    --- block are needed (name/author/author_url), and the script must stay
    dependency-free like the rest of scripts/.
    """
    fields: dict[str, str] = {}
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except OSError:
        return fields
    if not lines or lines[0].strip() != "---":
        return fields
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line[:1].isspace() or line.lstrip().startswith("#"):
            continue  # nested mapping entry or comment
        match = FRONTMATTER_FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def github_handle(url: str) -> str:
    """`https://github.com/<handle>[/repo]` -> handle, else ''."""
    if not url:
        return ""
    parts = urllib.parse.urlsplit(url)
    if (parts.hostname or "").lower() not in {"github.com", "www.github.com"}:
        return ""
    segments = [s for s in parts.path.split("/") if s]
    if not segments or not GITHUB_HANDLE_RE.fullmatch(segments[0]):
        return ""
    return segments[0]


def looks_like_placeholder(url: str) -> bool:
    """True for documentation examples that must not be fetched."""
    if not url.isascii():
        return True  # https://… and friends
    if any(ch in url for ch in "<>{}$"):
        return True
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    if not host or "." not in host or host in PLACEHOLDER_HOSTS:
        return True
    if PLACEHOLDER_UPPER_RE.search(parts.path + parts.query):
        return True
    segments = [s.lower() for s in parts.path.split("/") if s]
    values = [v.lower() for _, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)]
    if any(s in PLACEHOLDER_SEGMENTS for s in segments + values):
        return True
    # A query parameter left empty (`?accountOwner=`) is an unfinished example.
    return parts.query.endswith("=")


def extract_prose_urls(path: Path) -> list[tuple[str, int]]:
    """Non-Apify URLs used *outside* fenced code blocks, with line numbers.

    Fenced blocks hold sample payloads and CLI arguments — fetching those would
    check the author's example data, not the skill's links.
    """
    found: list[tuple[str, int]] = []
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if lint.FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in lint.URL_RE.finditer(line):
            url = lint.clean_url(match.group(0))
            if lint.is_apify_url(url) or looks_like_placeholder(url):
                continue
            found.append((url, lineno))
    return found


def load_catalog(selected: list[str]) -> tuple[list[Skill], int]:
    """Build the Skill list with all references already extracted."""
    skills: list[Skill] = []
    files_scanned = 0
    for skill_dir in lint.iter_skill_dirs(selected):
        skill = Skill(skill_dir)
        frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
        skill.author = frontmatter.get("author", "")
        skill.author_url = frontmatter.get("author_url", "")
        skill.files = lint.collect_md_files(skill_dir)
        files_scanned += len(skill.files)

        for md_file in skill.files:
            location_prefix = lint.rel(md_file)
            # actor-id already folds in store-url (apify.com/<owner>/<name>).
            for actor_id, _, lineno in lint.extract_refs(skill_dir, md_file)["actor-id"]:
                skill.actor_ids.setdefault(actor_id, []).append(f"{location_prefix}:{lineno}")
            for url, lineno in extract_prose_urls(md_file):
                skill.external_urls.setdefault(url, []).append(f"{location_prefix}:{lineno}")

        skills.append(skill)
    return skills, files_scanned


# --- network --------------------------------------------------------------


class HostThrottle:
    """Keep at least `interval` seconds between requests to the same host.

    51 skills produce a few hundred requests, most of them to two hosts
    (api.apify.com, github.com). Without this, a scheduled run reads as a burst
    and starts collecting 429s, which would turn the whole report into noise.
    """

    def __init__(self, interval: float):
        self.interval = interval
        self._lock = threading.Lock()
        self._next_free: dict[str, float] = {}

    def wait(self, host: str) -> None:
        if self.interval <= 0:
            return
        with self._lock:
            now = time.monotonic()
            start = max(now, self._next_free.get(host, 0.0))
            self._next_free[host] = start + self.interval
        delay = start - now
        if delay > 0:
            time.sleep(delay)


class Checker:
    """HTTP checks with retries, throttling and a result cache."""

    def __init__(self, timeout: float, retries: int, throttle: HostThrottle):
        self.timeout = timeout
        self.retries = retries
        self.throttle = throttle
        self.requests = 0
        self._lock = threading.Lock()
        self._url_cache: dict[str, tuple[str, str]] = {}

    def _count(self) -> None:
        with self._lock:
            self.requests += 1

    def _request(self, url: str, method: str):
        request = urllib.request.Request(
            url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
        )
        return urllib.request.urlopen(request, timeout=self.timeout)

    def check_url(self, url: str) -> tuple[str, str]:
        """Return (status, detail); status: ok | dead | unverifiable.

        HEAD first (cheap), falling back to GET when a server rejects HEAD.
        404/410 and unresolvable hostnames are 'dead'; 403/429/5xx/timeouts are
        'unverifiable' — plenty of hosts simply refuse robots.
        """
        with self._lock:
            cached = self._url_cache.get(url)
        if cached:
            return cached

        result = ("unverifiable", "no attempt made")
        host = urllib.parse.urlsplit(url).hostname or ""
        for attempt in range(1 + self.retries):
            for method in ("HEAD", "GET"):
                self.throttle.wait(host)
                self._count()
                try:
                    with self._request(url, method) as response:
                        code = getattr(response, "status", 200)
                        result = ("ok", f"HTTP {code}")
                        break
                except urllib.error.HTTPError as exc:
                    if exc.code in (404, 410):
                        result = ("dead", f"HTTP {exc.code}")
                        break
                    if exc.code in (400, 403, 405, 501) and method == "HEAD":
                        continue  # server dislikes HEAD — retry the same URL with GET
                    result = ("unverifiable", f"HTTP {exc.code}")
                    break
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    reason = getattr(exc, "reason", exc)
                    if isinstance(reason, socket.gaierror):
                        result = ("dead", "host does not resolve")
                    else:
                        result = ("unverifiable", str(reason))
                    break
            if result[0] != "unverifiable":
                break
            if attempt < self.retries:
                time.sleep(1)

        with self._lock:
            self._url_cache[url] = result
        return result

    def check_actor(self, actor_id: str) -> tuple[str, dict | None, str]:
        """Apify Store status of one actor id (see lint_references)."""
        self.throttle.wait("api.apify.com")
        self._count()
        return lint.fetch_actor_status(actor_id)


# --- checks ---------------------------------------------------------------


def author_of(skill: Skill) -> dict[str, str]:
    return {
        "skill": skill.name,
        "name": skill.author,
        "handle": skill.author_handle,
        "url": skill.author_url,
    }


def location_key(location: str) -> tuple[str, int]:
    """Sort `file.md:12` before `file.md:103` (plain sort would not)."""
    file_part, _, line_part = location.rpartition(":")
    return (file_part, int(line_part)) if line_part.isdigit() else (location, 0)


def make_entry(kind: str, subject: str, detail: str, owners: list[tuple[Skill, list[str]]]) -> dict:
    """One finding/note, attributed to every skill that references `subject`.

    `authors` holds JSON strings until finalize_entries() — dicts are not
    hashable and entries get merged/deduplicated before rendering.
    """
    return {
        "kind": kind,
        "subject": subject,
        "detail": detail,
        "skills": sorted({skill.name for skill, _ in owners}),
        "authors": sorted(
            {json.dumps(author_of(skill), sort_keys=True) for skill, _ in owners}
        ),
        "locations": sorted(
            {loc for _, locations in owners for loc in locations}, key=location_key
        ),
    }


def merge_into(primary: list[dict], secondary: list[dict]) -> list[dict]:
    """Fold secondary entries about an already-reported subject into it.

    An author_url is usually also linked from the skill's prose, so the same
    dead URL surfaces from two checks. Report it once, with both sets of
    locations, instead of inflating the finding count.
    """
    by_subject = {entry["subject"]: entry for entry in primary}
    remaining: list[dict] = []
    for entry in secondary:
        target = by_subject.get(entry["subject"])
        if target is None:
            remaining.append(entry)
            continue
        target["skills"] = sorted(set(target["skills"]) | set(entry["skills"]))
        target["authors"] = sorted(set(target["authors"]) | set(entry["authors"]))
        target["locations"] = sorted(
            set(target["locations"]) | set(entry["locations"]), key=location_key
        )
    return remaining


def finalize_entries(entries: list[dict]) -> list[dict]:
    for entry in entries:
        entry["authors"] = [json.loads(a) for a in entry["authors"]]
    return sorted(entries, key=lambda e: (list(FINDING_KINDS).index(e["kind"])
                                          if e["kind"] in FINDING_KINDS else 99,
                                          e["subject"]))


def check_actors(skills: list[Skill], checker: Checker, workers: int) -> tuple[list[dict], list[dict]]:
    """Existence / visibility / deprecation for every unique actor id."""
    owners: dict[str, list[tuple[Skill, list[str]]]] = {}
    for skill in skills:
        for actor_id, locations in skill.actor_ids.items():
            owners.setdefault(actor_id, []).append((skill, locations))

    actor_ids = sorted(owners)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(checker.check_actor, actor_ids))

    findings: list[dict] = []
    notes: list[dict] = []
    for actor_id, (status, data, detail) in zip(actor_ids, results):
        where = owners[actor_id]
        if status == "missing":
            findings.append(make_entry(
                "actor-missing", actor_id,
                "not found on Apify Store (HTTP 404) — replace it with a live "
                "actor or drop the reference", where))
        elif status == "unavailable":
            notes.append(make_entry(
                "actor-unverifiable", actor_id,
                f"Apify API did not answer ({detail or 'network error'})", where))
        elif data is not None:
            if data.get("isPublic") is False:
                findings.append(make_entry(
                    "actor-private", actor_id,
                    "no longer public on Apify Store — users of this skill "
                    "cannot run it", where))
            if data.get("isDeprecated") is True:
                findings.append(make_entry(
                    "actor-deprecated", actor_id,
                    "marked deprecated by its author — point the skill at a "
                    "maintained alternative", where))
    return findings, notes


def check_author_urls(skills: list[Skill], checker: Checker, workers: int) -> tuple[list[dict], list[dict]]:
    owners: dict[str, list[tuple[Skill, list[str]]]] = {}
    for skill in skills:
        url = skill.author_url
        if not url or looks_like_placeholder(url):
            continue
        owners.setdefault(url, []).append((skill, [f"skills/{skill.name}/SKILL.md"]))

    urls = sorted(owners)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(checker.check_url, urls))

    findings: list[dict] = []
    notes: list[dict] = []
    for url, (status, detail) in zip(urls, results):
        where = owners[url]
        if status == "dead":
            findings.append(make_entry(
                "author-url-dead", url,
                f"author_url is unreachable ({detail})", where))
        elif status == "unverifiable":
            notes.append(make_entry(
                "author-url-unverifiable", url,
                f"could not verify author_url ({detail})", where))
    return findings, notes


def check_external_urls(skills: list[Skill], checker: Checker, workers: int) -> tuple[list[dict], list[dict]]:
    owners: dict[str, list[tuple[Skill, list[str]]]] = {}
    for skill in skills:
        for url, locations in skill.external_urls.items():
            owners.setdefault(url, []).append((skill, locations))

    urls = sorted(owners)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(checker.check_url, urls))

    findings: list[dict] = []
    notes: list[dict] = []
    for url, (status, detail) in zip(urls, results):
        where = owners[url]
        if status == "dead":
            findings.append(make_entry(
                "external-url-dead", url, f"link is dead ({detail})", where))
        elif status == "unverifiable":
            notes.append(make_entry(
                "external-url-unverifiable", url,
                f"could not verify link ({detail})", where))
    return findings, notes


# --- reporting ------------------------------------------------------------


def render_author(author: dict, mention: bool) -> str:
    handle = author.get("handle") or ""
    if handle:
        return f"@{handle}" if mention else f"`{handle}`"
    return author.get("name") or author.get("url") or "unknown"


def render_authors(entry: dict, mention: bool) -> str:
    rendered = sorted({render_author(a, mention) for a in entry["authors"]})
    return ", ".join(rendered) if rendered else "—"


def render_locations(entry: dict, limit: int = 3) -> str:
    locations = entry["locations"]
    shown = ", ".join(f"`{loc}`" for loc in locations[:limit])
    if len(locations) > limit:
        shown += f" (+{len(locations) - limit} more)"
    return shown or "—"


def render_markdown(report: dict, mention_authors: bool) -> str:
    counts = report["checked"]
    lines = [
        REPORT_MARKER,
        f"# Catalog revalidation — {report['generated_at'][:10]}",
        "",
        f"Swept **{counts['skills']} skills** / {counts['files']} markdown files in "
        f"{report['duration_seconds']:.0f} s "
        f"({counts['http_requests']} HTTP requests). Unique references checked: "
        f"{counts['actor_ids']} actor ids, {counts['author_urls']} author URLs, "
        f"{counts['external_urls']} external links.",
        "",
        f"**{len(report['findings'])} finding(s)**, "
        f"{len(report['notes'])} unverifiable.",
        "",
    ]
    if mention_authors:
        lines += ["Authors of the affected skills are @-mentioned below.", ""]
    else:
        lines += [
            "Author handles are shown in backticks, not as mentions — re-run the "
            "workflow with `mention_authors: true` to ping them.",
            "",
        ]

    if not report["findings"]:
        lines += ["No findings — every actor, author URL and external link "
                  "checked out.", ""]

    for kind, heading in FINDING_KINDS.items():
        entries = [e for e in report["findings"] if e["kind"] == kind]
        if not entries:
            continue
        lines += [
            f"## {heading} ({len(entries)})",
            "",
            "| Reference | Skill(s) | Author(s) | What to do | Where |",
            "| --- | --- | --- | --- | --- |",
        ]
        for entry in entries:
            lines.append(
                f"| `{entry['subject']}` | {', '.join(entry['skills'])} | "
                f"{render_authors(entry, mention_authors)} | {entry['detail']} | "
                f"{render_locations(entry)} |"
            )
        lines.append("")

    if report["notes"]:
        lines += [
            f"<details><summary>Unverifiable ({len(report['notes'])}) — network "
            "refused to answer, not necessarily broken</summary>",
            "",
            "| Reference | Skill(s) | Reason |",
            "| --- | --- | --- |",
        ]
        for entry in report["notes"]:
            lines.append(
                f"| `{entry['subject']}` | {', '.join(entry['skills'])} | "
                f"{entry['detail']} |"
            )
        lines += ["", "</details>", ""]

    lines += [
        "---",
        "",
        "Generated by `scripts/revalidate_catalog.py` "
        "(`.github/workflows/revalidate-catalog.yml`). Every item is advisory: "
        "the catalog is not blocked by this report.",
    ]
    return "\n".join(lines) + "\n"


# --- entrypoint -----------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("skills", nargs="*", metavar="SKILL_DIR",
                        help="skill directories to check (default: the whole catalog)")
    parser.add_argument("--json-out", metavar="PATH",
                        help="write the machine-readable report here (default: stdout)")
    parser.add_argument("--markdown-out", metavar="PATH",
                        help="write the markdown report here (default: stdout)")
    parser.add_argument("--mention-authors", action="store_true",
                        help="render author handles as live @mentions (pings people)")
    parser.add_argument("--skip-external", action="store_true",
                        help="skip author_url and external-link liveness (actors only)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"seconds per HTTP request (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                        help=f"extra attempts on transient failures (default: {DEFAULT_RETRIES})")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_WORKERS,
                        help=f"parallel in-flight requests (default: {DEFAULT_WORKERS})")
    parser.add_argument("--min-interval", type=float, default=DEFAULT_MIN_INTERVAL,
                        help="seconds between two requests to the same host "
                             f"(default: {DEFAULT_MIN_INTERVAL})")
    args = parser.parse_args()

    started = time.monotonic()
    skills, files_scanned = load_catalog(args.skills)
    checker = Checker(args.timeout, args.retries, HostThrottle(args.min_interval))
    workers = max(1, args.max_workers)

    findings, notes = check_actors(skills, checker, workers)
    if not args.skip_external:
        author_findings, author_notes = check_author_urls(skills, checker, workers)
        external_findings, external_notes = check_external_urls(skills, checker, workers)
        # An author_url linked from prose must not be counted twice.
        external_findings = merge_into(author_findings, external_findings)
        external_notes = merge_into(author_notes, external_notes)
        findings.extend(author_findings + external_findings)
        notes.extend(author_notes + external_notes)

    author_urls = {s.author_url for s in skills if s.author_url}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": round(time.monotonic() - started, 1),
        "external_checks": not args.skip_external,
        "checked": {
            "skills": len(skills),
            "files": files_scanned,
            "actor_ids": len({a for s in skills for a in s.actor_ids}),
            "author_urls": len(author_urls),
            "external_urls": len({u for s in skills for u in s.external_urls}),
            "http_requests": checker.requests,
        },
        "findings": finalize_entries(findings),
        "notes": finalize_entries(notes),
    }
    report["counts"] = {
        "findings": len(report["findings"]),
        "notes": len(report["notes"]),
    }

    markdown = render_markdown(report, args.mention_authors)
    json_text = json.dumps(report, indent=2, sort_keys=False)

    if args.json_out:
        Path(args.json_out).write_text(json_text + "\n", encoding="utf-8")
    if args.markdown_out:
        Path(args.markdown_out).write_text(markdown, encoding="utf-8")
    if not args.json_out and not args.markdown_out:
        print(json_text)
        print()
        print(markdown)
    elif not args.markdown_out:
        print(markdown)
    elif not args.json_out:
        print(json_text)

    print(
        f"revalidate: {report['counts']['findings']} finding(s), "
        f"{report['counts']['notes']} unverifiable, "
        f"{report['checked']['http_requests']} request(s) in "
        f"{report['duration_seconds']} s",
        file=sys.stderr,
    )
    return 0  # advisory by design — never fails the run


if __name__ == "__main__":
    sys.exit(main())
