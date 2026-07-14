#!/usr/bin/env python3
"""Validate, render, and audit the Android Performance Ecosystem catalog."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "ecosystem.json"
MARKER_START = "<!-- android-performance-ecosystem:start -->"
MARKER_END = "<!-- android-performance-ecosystem:end -->"
LANGUAGES = {"en", "zh-CN"}
EXPECTED_PROJECT_IDS = {
    "tracefix",
    "perfetto-tools",
    "smartperfetto",
    "perfetto-skills",
    "android-performance-blog",
    "android-internal-wiki",
    "trace-for-blog",
}


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if catalog.get("official_affiliation") is not False:
        errors.append("official_affiliation must remain false")

    projects = catalog.get("projects")
    if not isinstance(projects, list):
        return errors + ["projects must be a list"]

    ids = [project.get("id") for project in projects if isinstance(project, dict)]
    if set(ids) != EXPECTED_PROJECT_IDS or len(ids) != len(EXPECTED_PROJECT_IDS):
        errors.append("catalog must contain each of the seven core projects exactly once")
    if len(ids) != len(set(ids)):
        errors.append("project ids must be unique")

    public_urls: list[str] = []
    for index, project in enumerate(projects):
        prefix = f"projects[{index}]"
        if not isinstance(project, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not project.get("name"):
            errors.append(f"{prefix}.name is required")
        for field in ("stage", "role"):
            localized = project.get(field)
            if not isinstance(localized, dict) or set(localized) != LANGUAGES:
                errors.append(f"{prefix}.{field} must contain exactly en and zh-CN")

        availability = project.get("availability")
        public_url = project.get("public_url")
        readmes = project.get("readmes")
        if availability == "public":
            if not isinstance(public_url, str) or not public_url.startswith("https://github.com/"):
                errors.append(f"{prefix}.public_url must be a GitHub HTTPS URL")
            else:
                public_urls.append(public_url)
            if not project.get("default_branch"):
                errors.append(f"{prefix}.default_branch is required for public projects")
            if not isinstance(readmes, list) or not readmes:
                errors.append(f"{prefix}.readmes must list public root READMEs")
            else:
                for readme in readmes:
                    if readme.get("language") not in LANGUAGES:
                        errors.append(f"{prefix}.readmes has an unsupported language")
                    path = readme.get("path")
                    if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts:
                        errors.append(f"{prefix}.readmes has an unsafe path")
        elif availability == "coming_soon":
            if public_url is not None or project.get("site_url") is not None:
                errors.append(f"{prefix} coming-soon project must not expose a URL")
            if project.get("default_branch") is not None or readmes != []:
                errors.append(f"{prefix} coming-soon project must not expose repository metadata")
        else:
            errors.append(f"{prefix}.availability must be public or coming_soon")

    if len(public_urls) != len(set(public_urls)):
        errors.append("public project URLs must be unique")

    return errors


def render_snippet(catalog: dict[str, Any], language: str) -> str:
    if language not in LANGUAGES:
        raise ValueError(f"unsupported language: {language}")

    if language == "en":
        heading = "## Android performance ecosystem"
        intro = (
            "This repository is one part of the "
            "[Android Performance Ecosystem](https://github.com/Gracker/android-performance-ecosystem): "
            "an optional path from instrumentation and capture to analysis, system knowledge, and reproducible cases."
        )
        headers = ("Stage", "Project", "Purpose", "Address")
        coming_soon = "**Coming soon**"
        github_label = "GitHub"
        website_label = "Website"
    else:
        heading = "## Android 性能分析生态"
        intro = (
            "本仓库属于 [Android Performance Ecosystem](https://github.com/Gracker/android-performance-ecosystem)："
            "它把可选插桩、采集、分析、系统知识与可复现案例连接成一套完整路径。"
        )
        headers = ("阶段", "项目", "作用", "地址")
        coming_soon = "**Coming soon**"
        github_label = "GitHub"
        website_label = "网站"

    lines = [
        MARKER_START,
        heading,
        "",
        intro,
        "",
        f"| {headers[0]} | {headers[1]} | {headers[2]} | {headers[3]} |",
        "| --- | --- | --- | --- |",
    ]
    for project in catalog["projects"]:
        url = project["public_url"]
        name = project["name"]
        project_cell = f"[{name}]({url})" if url else name
        if url:
            address = f"[{github_label}]({url})"
            if project.get("site_url"):
                address += f" · [{website_label}]({project['site_url']})"
        else:
            address = coming_soon
        lines.append(
            f"| {project['stage'][language]} | {project_cell} | "
            f"{project['role'][language]} | {address} |"
        )
    lines.extend([MARKER_END, ""])
    return "\n".join(lines)


def extract_marker_block(text: str) -> str:
    start = text.find(MARKER_START)
    end = text.find(MARKER_END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("ecosystem marker block is missing or malformed")
    end += len(MARKER_END)
    if text.find(MARKER_START, start + len(MARKER_START)) >= 0:
        raise ValueError("multiple ecosystem marker blocks found")
    return text[start:end].strip()


def check_readme_text(text: str, expected: str, label: str) -> list[str]:
    try:
        actual = extract_marker_block(text)
    except ValueError as exc:
        return [f"{label}: {exc}"]
    if actual != expected.strip():
        return [f"{label}: ecosystem marker block has drifted from ecosystem.json"]
    return []


def public_targets(catalog: dict[str, Any]):
    for project in catalog["projects"]:
        if project["availability"] != "public":
            continue
        owner, repo = project["public_url"].removeprefix("https://github.com/").split("/", 1)
        for readme in project["readmes"]:
            yield {
                "owner": owner,
                "repo": repo,
                "branch": project["default_branch"],
                "path": readme["path"],
                "language": readme["language"],
            }


def fetch_text(url: str, attempts: int = 3) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "android-performance-ecosystem-validator"})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def validate_local_files(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_by_language = {language: render_snippet(catalog, language) for language in LANGUAGES}
    for language in sorted(LANGUAGES):
        snippet_path = ROOT / "snippets" / f"ecosystem.{language}.md"
        if not snippet_path.is_file():
            errors.append(f"missing generated snippet: {snippet_path.relative_to(ROOT)}")
        elif snippet_path.read_text(encoding="utf-8") != expected_by_language[language]:
            errors.append(f"generated snippet is stale: {snippet_path.relative_to(ROOT)}")

    for path, language in ((ROOT / "README.md", "en"), (ROOT / "README.zh-CN.md", "zh-CN")):
        if not path.is_file():
            errors.append(f"missing hub README: {path.name}")
        else:
            errors.extend(check_readme_text(path.read_text(encoding="utf-8"), expected_by_language[language], path.name))

    return errors


def write_snippets(catalog: dict[str, Any]) -> None:
    snippet_dir = ROOT / "snippets"
    snippet_dir.mkdir(parents=True, exist_ok=True)
    for language in sorted(LANGUAGES):
        (snippet_dir / f"ecosystem.{language}.md").write_text(
            render_snippet(catalog, language), encoding="utf-8"
        )


def print_errors(errors: list[str]) -> int:
    if not errors:
        print("OK")
        return 0
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def command_validate(catalog: dict[str, Any]) -> int:
    errors = validate_catalog(catalog)
    if not errors:
        errors.extend(validate_local_files(catalog))
    return print_errors(errors)


def command_check_readmes(catalog: dict[str, Any], remote: bool, targets: list[str]) -> int:
    errors = validate_catalog(catalog)
    expected = {language: render_snippet(catalog, language) for language in LANGUAGES}
    if remote:
        for target in public_targets(catalog):
            url = (
                f"https://raw.githubusercontent.com/{target['owner']}/{target['repo']}/"
                f"{target['branch']}/{target['path']}"
            )
            label = f"{target['owner']}/{target['repo']}:{target['path']}"
            try:
                text = fetch_text(url)
            except RuntimeError as exc:
                errors.append(str(exc))
                continue
            errors.extend(check_readme_text(text, expected[target["language"]], label))
    for raw_target in targets:
        try:
            language, raw_path = raw_target.split("=", 1)
        except ValueError:
            errors.append(f"invalid --target {raw_target!r}; expected LANGUAGE=PATH")
            continue
        if language not in LANGUAGES:
            errors.append(f"invalid --target language: {language}")
            continue
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            errors.append(f"local README not found: {path}")
            continue
        errors.extend(check_readme_text(path.read_text(encoding="utf-8"), expected[language], str(path)))
    return print_errors(errors)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate catalog, snippets, privacy rules, and hub READMEs")

    render_parser = subparsers.add_parser("render", help="render a README marker block")
    render_parser.add_argument("--language", choices=sorted(LANGUAGES), required=True)

    subparsers.add_parser("write-snippets", help="regenerate snippets from ecosystem.json")

    check_parser = subparsers.add_parser("check-readmes", help="check README marker blocks")
    check_parser.add_argument("--remote", action="store_true", help="check all public repositories")
    check_parser.add_argument(
        "--target",
        action="append",
        default=[],
        metavar="LANGUAGE=PATH",
        help="check a local README; may be repeated",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    catalog = load_catalog()
    if args.command == "validate":
        return command_validate(catalog)
    if args.command == "render":
        errors = validate_catalog(catalog)
        if errors:
            return print_errors(errors)
        print(render_snippet(catalog, args.language), end="")
        return 0
    if args.command == "write-snippets":
        errors = validate_catalog(catalog)
        if errors:
            return print_errors(errors)
        write_snippets(catalog)
        return 0
    if args.command == "check-readmes":
        return command_check_readmes(catalog, args.remote, args.target)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
