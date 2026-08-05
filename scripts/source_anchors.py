#!/usr/bin/env python3
"""Общий разбор якорей на текст книги для валидатора и генератора lock-файла."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

PLUGIN_NAME = "developing-ai-agents"
SKILL_DIRECTORY = Path("plugins") / PLUGIN_NAME / "skills" / PLUGIN_NAME
SOURCE_BOOK_DIRECTORY = SKILL_DIRECTORY / "references" / "source-book"
LOCK_RELATIVE_PATH = SKILL_DIRECTORY / "references" / "source-map.lock.json"

LOCAL_SOURCE_ANCHOR = re.compile(
    r"(?<![-\w/])(?P<path>references/source-book/[A-Za-z0-9._/-]+\.md):"
    r"(?P<start>\d+)(?:-(?P<end>\d+))?"
)
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s")

_DASHES = str.maketrans({"–": "-", "—": "-", "―": "-", "−": "-"})
_QUOTES = str.maketrans(
    {"«": '"', "»": '"', "“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"}
)


def anchor_key(path: str, start: int) -> str:
    """Ключ якоря в lock-файле: имя файла книги и номер строки."""
    return f"{Path(path).name}:{start}"


def normalize(text: str) -> str:
    """Свести типографские варианты и пробелы к сравнимому виду."""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.translate(_DASHES).translate(_QUOTES)
    return " ".join(normalized.split())


def section_text(lines: list[str], start: int) -> str:
    """Текст секции якоря: от заголовка на строке ``start`` до следующего
    заголовка любого уровня.

    Граница проходит по ближайшему заголовку, а не по заголовку того же уровня.
    Раздел ``##`` вместе с вложенными ``###`` в этой книге достигает 42 000
    символов, поэтому цитата из чужого подраздела прошла бы проверку. Обрыв на
    ближайшем заголовке заставляет ссылаться на тот подраздел, откуда цитата
    действительно взята.

    Если якорь указывает не на заголовок, секцией считается сама строка:
    расширять окно нечем, а брать соседние абзацы означало бы принимать цитату
    не из того места.
    """
    if start < 1 or start > len(lines):
        return ""
    if HEADING.match(lines[start - 1]) is None:
        return normalize(lines[start - 1])
    collected = [lines[start - 1]]
    for line in lines[start:]:
        if HEADING.match(line) is not None:
            break
        collected.append(line)
    return normalize(" ".join(collected))


def iter_skill_documents(root: Path) -> list[Path]:
    """Markdown-файлы скилла, кроме самого текста книги."""
    skill_root = root / SKILL_DIRECTORY
    if not skill_root.is_dir():
        return []
    return [
        path
        for path in sorted(skill_root.rglob("*.md"))
        if SOURCE_BOOK_DIRECTORY.name not in path.parts
    ]
