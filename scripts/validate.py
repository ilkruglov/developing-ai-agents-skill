#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

PLUGIN_NAME = "developing-ai-agents"
MARKETPLACE_NAME = "developing-ai-agents-skill"
PLUGIN_DIRECTORY = Path("plugins") / PLUGIN_NAME
PLUGIN_SOURCE = f"./{PLUGIN_DIRECTORY.as_posix()}"
SKILL_DIRECTORY = PLUGIN_DIRECTORY / "skills" / PLUGIN_NAME

REQUIRED_PATHS = (
    ".agents/plugins/marketplace.json",
    str(PLUGIN_DIRECTORY / ".codex-plugin" / "plugin.json"),
    str(PLUGIN_DIRECTORY / "LICENSE"),
    str(PLUGIN_DIRECTORY / "NOTICE"),
    str(PLUGIN_DIRECTORY / "SOURCE.json"),
    str(PLUGIN_DIRECTORY / "evals" / "benchmark-v2.json"),
    str(PLUGIN_DIRECTORY / "benchmarks" / "v2" / "benchmark.json"),
    str(SKILL_DIRECTORY / "SKILL.md"),
    "README.md",
    "LICENSE",
    "NOTICE",
    "SOURCE.json",
    str(SKILL_DIRECTORY / "agents" / "openai.yaml"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "introduction.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter1.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter2.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter3.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter4.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter5.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter6.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter7.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter8.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter9.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "chapter10.md"),
    str(SKILL_DIRECTORY / "references" / "source-book" / "afterword.md"),
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
    str(PLUGIN_DIRECTORY / "NOTICE"): (
        "Bojie Li",
        "https://github.com/bojieli",
        "https://github.com/bojieli/ai-agent-book",
        "https://github.com/ilkruglov/ai-agent-book",
    ),
    str(PLUGIN_DIRECTORY / "SOURCE.json"): (
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
    source_root = root / SKILL_DIRECTORY / "references" / "source-book"
    return [
        path
        for path in root.rglob("*.md")
        if source_root not in path.parents and ".git" not in path.parts
    ]


def iter_source_anchor_documents(root: Path) -> list[Path]:
    documents = iter_markdown_documents(root)
    evals_root = root / PLUGIN_DIRECTORY / "evals"
    if evals_root.is_dir():
        documents.extend(evals_root.rglob("*.json"))
        documents.extend(evals_root.rglob("*.jsonl"))
    return sorted(set(documents))


def validate_marketplace(root: Path, errors: list[str]) -> None:
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace_path.is_file():
        return
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(marketplace, dict):
        return
    if marketplace.get("name") != MARKETPLACE_NAME:
        errors.append(f"invalid marketplace name: expected {MARKETPLACE_NAME}")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("invalid marketplace plugin source: plugins must be an array")
        return

    entry = next(
        (
            value
            for value in plugins
            if isinstance(value, dict) and value.get("name") == PLUGIN_NAME
        ),
        None,
    )
    source = entry.get("source") if isinstance(entry, dict) else None
    source_path = source.get("path") if isinstance(source, dict) else None
    resolved_source = root / str(source_path).removeprefix("./")
    if source_path != PLUGIN_SOURCE or not resolved_source.is_dir():
        errors.append(
            "invalid marketplace plugin source: expected "
            f"{PLUGIN_NAME} at {PLUGIN_SOURCE}"
        )


def validate_plugin_manifest(root: Path, errors: list[str]) -> None:
    manifest_path = root / PLUGIN_DIRECTORY / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(manifest, dict):
        return
    if manifest.get("name") != PLUGIN_NAME or manifest.get("skills") != "./skills/":
        errors.append(
            "invalid plugin manifest: expected name developing-ai-agents "
            "and skills path ./skills/"
        )


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

    skill_path = root / SKILL_DIRECTORY / "SKILL.md"
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

    validate_marketplace(root, errors)
    validate_plugin_manifest(root, errors)

    for document_path in iter_source_anchor_documents(root):
        text = document_path.read_text(encoding="utf-8")
        for match in NON_LOCAL_SOURCE_PATH.finditer(text):
            relative_path = document_path.relative_to(root)
            errors.append(
                f"non-local source anchor in {relative_path}: {match.group(0)}"
            )
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
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
        description="Validate the developing-ai-agents plugin repository"
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
