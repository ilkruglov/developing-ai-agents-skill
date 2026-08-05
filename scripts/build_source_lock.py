#!/usr/bin/env python3
"""Собрать lock-файл якорей на текст книги.

Валидатор не обновляет lock самостоятельно: расхождение — ошибка. Обновление
выполняется только этим скриптом и попадает в diff отдельным изменением,
поэтому сдвиг текста книги нельзя «залечить» незаметно для ревьюера.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from source_anchors import (
    HEADING,
    LOCAL_SOURCE_ANCHOR,
    LOCK_RELATIVE_PATH,
    SKILL_DIRECTORY,
    anchor_key,
    iter_skill_documents,
)

UPSTREAM_COMMIT = "97de455e9aa44cf9f93441ce0c771c9aa9643d92"
TRANSLATION_COMMIT = "ed2ae516d45dfe26e934cb390b80f105ca780b1f"
LINE_TEXT_LIMIT = 200


def build_lock(root: Path) -> dict:
    anchors: dict[str, dict[str, str]] = {}
    line_cache: dict[Path, list[str]] = {}
    for document in iter_skill_documents(root):
        text = document.read_text(encoding="utf-8")
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
            if not source_path.is_file():
                continue
            if source_path not in line_cache:
                line_cache[source_path] = source_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            lines = line_cache[source_path]
            start = int(match.group("start"))
            if start < 1 or start > len(lines):
                continue
            line = lines[start - 1]
            anchors[anchor_key(match.group("path"), start)] = {
                "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "line_text": line[:LINE_TEXT_LIMIT],
                "kind": "heading" if HEADING.match(line) else "inline",
            }
    return {
        "schema_version": 1,
        "book": {
            "upstream_commit": UPSTREAM_COMMIT,
            "translation_commit": TRANSLATION_COMMIT,
        },
        "anchors": dict(sorted(anchors.items())),
        "allowed_inline": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the source anchor lock file")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    arguments = parser.parse_args()

    root = arguments.root.resolve()
    lock = build_lock(root)
    lock_path = root / LOCK_RELATIVE_PATH
    lock_path.write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(lock['anchors'])} anchors to {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
