#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

REQUIRED_PATHS = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "SOURCE.json",
    "agents/openai.yaml",
    "references/source-book/introduction.md",
    "references/source-book/chapter1.md",
    "references/source-book/chapter2.md",
    "references/source-book/chapter3.md",
    "references/source-book/chapter4.md",
    "references/source-book/chapter5.md",
    "references/source-book/chapter6.md",
    "references/source-book/chapter7.md",
    "references/source-book/chapter8.md",
    "references/source-book/chapter9.md",
    "references/source-book/chapter10.md",
    "references/source-book/afterword.md",
)
REQUIRED_ATTRIBUTIONS = {
    "README.md": (
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    "NOTICE": (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    "SOURCE.json": (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
}
NON_LOCAL_SOURCE_PATH = re.compile(r"(?<![-\w/])book/")
LOCAL_SOURCE_ANCHOR = re.compile(
    r"(?<![-\w/])(?P<path>references/source-book/[A-Za-z0-9._/-]+\.md):"
    r"(?P<start>\d+)(?:-(?P<end>\d+))?"
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")


def parse_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.split("#", maxsplit=1)[0])


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}

    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        if ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        values[key.strip()] = value.strip()
    return {}


def iter_markdown_documents(root: Path) -> list[Path]:
    source_root = root / "references" / "source-book"
    return [
        path
        for path in root.rglob("*.md")
        if source_root not in path.parents and ".git" not in path.parts
    ]


def iter_source_anchor_documents(root: Path) -> list[Path]:
    documents = iter_markdown_documents(root)
    evals_root = root / "evals"
    if evals_root.is_dir():
        documents.extend(evals_root.rglob("*.json"))
        documents.extend(evals_root.rglob("*.jsonl"))
    return sorted(set(documents))


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    line_counts: dict[Path, int] = {}
    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    for relative_path, required_values in REQUIRED_ATTRIBUTIONS.items():
        path = root / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for required_value in required_values:
            if required_value not in text:
                errors.append(
                    f"missing attribution in {relative_path}: {required_value}"
                )

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        frontmatter = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        if frontmatter.get("name") != "developing-ai-agents" or not frontmatter.get(
            "description"
        ):
            errors.append(
                "invalid SKILL.md frontmatter: expected name "
                "developing-ai-agents and a non-empty description"
            )

    for json_path in root.rglob("*.json"):
        relative_path = json_path.relative_to(root)
        if ".git" in relative_path.parts or ".tmp" in relative_path.parts:
            continue
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid JSON in {relative_path}: {error}")

    for jsonl_path in root.rglob("*.jsonl"):
        relative_path = jsonl_path.relative_to(root)
        if ".git" in relative_path.parts or ".tmp" in relative_path.parts:
            continue
        for line_number, line in enumerate(
            jsonl_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(
                    f"invalid JSONL in {relative_path}:{line_number}: {error}"
                )

    for document_path in iter_source_anchor_documents(root):
        text = document_path.read_text(encoding="utf-8")
        for match in NON_LOCAL_SOURCE_PATH.finditer(text):
            relative_path = document_path.relative_to(root)
            errors.append(
                f"non-local source anchor in {relative_path}: {match.group(0)}"
            )
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / match.group("path")
            start = int(match.group("start"))
            end = int(match.group("end") or start)
            if not source_path.is_file():
                errors.append(f"source anchor file missing: {match.group('path')}")
                continue
            if source_path not in line_counts:
                line_counts[source_path] = len(
                    source_path.read_text(encoding="utf-8").splitlines()
                )
            maximum = line_counts[source_path]
            if start < 1 or end < start or end > maximum:
                errors.append(
                    "source anchor out of range: "
                    f"{match.group(0)} (file has {maximum} lines)"
                )

    for markdown_path in iter_markdown_documents(root):
        text = markdown_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = parse_link_target(match.group("target"))
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved_target = (markdown_path.parent / target).resolve()
            if not resolved_target.exists():
                relative_path = markdown_path.relative_to(root)
                errors.append(
                    f"broken Markdown link in {relative_path}: {match.group('target')}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the autonomous skill repository"
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
