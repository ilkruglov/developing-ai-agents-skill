#!/usr/bin/env python3
"""Переписать показанный вывод калькулятора в документах скилла.

Документы показывают команды `python3 scripts/eval_calc.py …` в блоке кода и
сразу за ним — блок ```text с выводом, вставленным как есть; тест
tests/test_doc_commands.py сверяет его побайтно. Когда меняется текст
вывода, блоки переписывает этот скрипт, а не рука: так вывод в документе
остаётся фактическим.

    python3 scripts/update_calc_docs.py            # переписать все документы
    python3 scripts/update_calc_docs.py --check    # только сообщить, код 1
    python3 scripts/update_calc_docs.py путь.md    # отдельные файлы

Строка-маркер `<<CALC аргументы>>` разворачивается в блок команды
`python3 scripts/eval_calc.py аргументы` и блок её вывода — так новая
команда добавляется в документ без ручного копирования. Блок команд без
блока вывода получает его. Маркер внутри блока кода — пример синтаксиса,
он остаётся как есть; маркер с отступом — ошибка: развёрнутый с отступом
блок перестал бы быть блоком кода. Команды запускаются из каталога скилла.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "developing-ai-agents" / "skills" / "developing-ai-agents"
PREFIX = "python3 scripts/eval_calc.py"

FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
MARKER = re.compile(r"^(?P<indent>\s*)<<CALC (?P<args>.+)>>\s*$")
DESCRIPTION = "Переписать показанный вывод калькулятора в документах скилла."


@dataclass
class Block:
    line: int  # номер строки открывающего забора, с 1
    info: str
    lines: list[str]
    end: int  # номер строки закрывающего забора


@dataclass
class CommandBlock:
    line: int
    end: int
    commands: list[str]
    expected: list[str] | None
    expected_line: int | None  # открывающий забор блока вывода
    expected_end: int | None  # закрывающий забор блока вывода


def documents() -> list[Path]:
    """SKILL.md и references/**/*.md, кроме полного текста книги."""
    references = [
        path
        for path in sorted((SKILL / "references").rglob("*.md"))
        if "source-book" not in path.relative_to(SKILL).parts
    ]
    return [SKILL / "SKILL.md", *references]


def parse_blocks(text: str) -> tuple[list[Block], set[int]]:
    """Блоки кода (заборы ``` и ~~~) и номера строк внутри них, с заборами."""
    lines = text.splitlines()
    blocks: list[Block] = []
    inside: set[int] = set()
    index = 0
    while index < len(lines):
        match = FENCE_OPEN.match(lines[index])
        if not match:
            index += 1
            continue
        fence = match.group("fence")
        closing = re.compile(rf"^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*$")
        end = index + 1
        while end < len(lines) and not closing.match(lines[end]):
            end += 1
        blocks.append(
            Block(
                index + 1, match.group("info").strip(), lines[index + 1 : end], end + 1
            )
        )
        inside.update(range(index + 1, end + 2))
        index = end + 1
    return blocks, inside


def command_blocks(text: str) -> list[CommandBlock]:
    """Блоки с командами калькулятора и блоки ```text, идущие сразу за ними."""
    blocks, _ = parse_blocks(text)
    lines = text.splitlines()
    found: list[CommandBlock] = []
    for index, block in enumerate(blocks):
        commands = [
            line.strip()
            for line in block.lines
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not any(command.startswith(PREFIX) for command in commands):
            continue
        item = CommandBlock(block.line, block.end, commands, None, None, None)
        if index + 1 < len(blocks):
            following = blocks[index + 1]
            between = lines[block.end : following.line - 1]
            if following.info == "text" and not any(s.strip() for s in between):
                item.expected = following.lines
                item.expected_line = following.line
                item.expected_end = following.end
        found.append(item)
    return found


def run_command(command: str) -> str:
    """Вывод команды калькулятора, запущенной из каталога скилла."""
    arguments = shlex.split(command)
    if arguments[:2] != ["python3", "scripts/eval_calc.py"]:
        raise ValueError(f"не команда калькулятора: {command}")
    result = subprocess.run(
        [sys.executable, *arguments[1:]],
        cwd=SKILL,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"команда завершилась с кодом {result.returncode}: {command}\n"
            f"{result.stderr.strip()}"
        )
    return result.stdout


def expand_markers(text: str) -> str:
    """Маркеры `<<CALC …>>` вне блоков кода — в блоки команд."""
    _, inside = parse_blocks(text)
    lines = []
    for number, line in enumerate(text.splitlines(), 1):
        match = MARKER.match(line)
        if match is None or number in inside:
            lines.append(line)
            continue
        if match.group("indent"):
            raise ValueError(
                f"маркер с отступом в строке {number}: ставьте <<CALC …>> с начала "
                "строки"
            )
        lines += ["```bash", f"{PREFIX} {match.group('args')}", "```"]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def update_text(text: str, run: Callable[[str], str]) -> str:
    """Текст документа с фактическим выводом под каждым блоком команд."""
    text = expand_markers(text)
    lines = text.splitlines()
    # с конца, чтобы правки не сдвигали номера строк ещё не обработанных блоков
    for block in reversed(command_blocks(text)):
        output = "\n\n".join(run(command).rstrip("\n") for command in block.commands)
        shown = output.split("\n")
        if block.expected_line is not None and block.expected_end is not None:
            lines[block.expected_line : block.expected_end - 1] = shown
        else:
            lines[block.end : block.end] = ["", "```text", *shown, "```"]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--check", action="store_true", help="не писать, код 1 при расхождении"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="документы; по умолчанию все документы скилла",
    )
    arguments = parser.parse_args(argv)
    paths = [path.resolve() for path in arguments.paths] or documents()

    stale = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        try:
            updated = update_text(text, run_command)
        except (ValueError, RuntimeError) as error:
            print(f"ошибка: {path}: {error}", file=sys.stderr)
            return 2
        if updated == text:
            continue
        stale.append(path)
        if not arguments.check:
            path.write_text(updated, encoding="utf-8")
    verb = "устарел вывод" if arguments.check else "переписан вывод"
    for path in stale:
        print(f"{verb}: {path}")
    return 1 if arguments.check and stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
