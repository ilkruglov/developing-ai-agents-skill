"""Команды калькулятора из документов скилла выполняются и дают показанный вывод.

Проверяются SKILL.md и references/**/*.md, кроме полного текста книги
(references/source-book/). Команды запускаются из каталога скилла, как их
запускает агент.

1. Блоки кода. Блок, где есть строка `python3 scripts/eval_calc.py …`, —
   блок команд: все его непустые строки (кроме комментариев `#`) обязаны
   быть такими командами. Каждая команда запускается; ненулевой код
   возврата — ошибка. Сразу за блоком (через пустые строки) обязан идти
   блок `text` — показанный вывод. Он сверяется с фактическим выводом
   побайтно (выводы нескольких команд блока идут подряд через пустую
   строку): документ обещает, что вывод вставлен как есть, и любое
   расхождение — либо устаревший документ, либо изменившийся расчёт.
2. Инлайн-команды. Спан `python3 scripts/eval_calc.py …` вне блоков без
   подстановок (`<…>`, `…`) — полная команда: она запускается, сверяется
   код возврата.
3. Фрагменты. Спан вида `eval_calc.py noise` или `scripts/eval_calc.py`
   без `python3` — ссылка в тексте. Её не запускают, но названная команда
   обязана существовать, а флаги — быть в её `--help`: переименование
   команды или флага не пройдёт незамеченным.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import unittest
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "developing-ai-agents" / "skills" / "developing-ai-agents"
PREFIX = "python3 scripts/eval_calc.py"
COMMANDS = ("passk", "interval", "sample-size", "compare", "noise")
TIMEOUT_SECONDS = 30

FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
INLINE = re.compile(r"(?<!`)`(?P<code>[^`\n]+)`(?!`)")
FRAGMENT = re.compile(
    r"(?<![\w/])(?:scripts/)?eval_calc\.py(?:\s+(?P<command>[a-z][\w-]*))?"
    r"(?P<rest>[^`]*)"
)
FLAG = re.compile(r"(?<![\w-])--[a-z][\w-]*")
PLACEHOLDER = re.compile(r"<[^>]+>|…|\.\.\.")


@dataclass
class Block:
    path: str
    line: int
    info: str
    lines: list[str]
    end: int  # номер строки закрывающего забора


@dataclass
class CommandBlock:
    path: str
    line: int
    commands: list[str]
    expected: list[str] | None
    expected_line: int | None


def documents() -> list[Path]:
    references = [
        path
        for path in sorted((SKILL / "references").rglob("*.md"))
        if "source-book" not in path.relative_to(SKILL).parts
    ]
    return [SKILL / "SKILL.md", *references]


def parse_blocks(text: str, label: str) -> tuple[list[Block], set[int]]:
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
                label,
                index + 1,
                match.group("info").strip(),
                lines[index + 1 : end],
                end + 1,
            )
        )
        inside.update(range(index + 1, end + 2))
        index = end + 1
    return blocks, inside


def command_blocks_in(text: str, label: str) -> list[CommandBlock]:
    blocks, _ = parse_blocks(text, label)
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
        expected: list[str] | None = None
        expected_line: int | None = None
        if index + 1 < len(blocks):
            following = blocks[index + 1]
            between = lines[block.end : following.line - 1]
            if following.info == "text" and not any(s.strip() for s in between):
                expected = following.lines
                expected_line = following.line
        found.append(CommandBlock(label, block.line, commands, expected, expected_line))
    return found


def label(path: Path) -> str:
    return path.relative_to(SKILL).as_posix()


def command_blocks() -> list[CommandBlock]:
    found: list[CommandBlock] = []
    for path in documents():
        found += command_blocks_in(path.read_text(encoding="utf-8"), label(path))
    return found


def inline_spans() -> Iterator[tuple[str, int, str]]:
    for path in documents():
        text = path.read_text(encoding="utf-8")
        _, inside = parse_blocks(text, label(path))
        for number, line in enumerate(text.splitlines(), 1):
            if number in inside:
                continue
            for match in INLINE.finditer(line):
                yield label(path), number, match.group("code").strip()


@cache
def run(command: str) -> subprocess.CompletedProcess[str]:
    arguments = shlex.split(command)
    assert arguments[:2] == ["python3", "scripts/eval_calc.py"], command
    try:
        return subprocess.run(
            [sys.executable, *arguments[1:]],
            cwd=SKILL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            command, 124, "", f"тайм-аут {TIMEOUT_SECONDS} s"
        )


def shown_output(block: CommandBlock) -> str:
    """Фактический вывод блока в том виде, в каком его вставляют в документ."""
    return "\n\n".join(run(command).stdout.rstrip("\n") for command in block.commands)


class DocCommandsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blocks = command_blocks()
        spans = list(inline_spans())
        cls.inline = [
            (path, line, code) for path, line, code in spans if code.startswith(PREFIX)
        ]
        cls.fragments = [
            (path, line, code)
            for path, line, code in spans
            if not code.startswith("python3 ") and FRAGMENT.search(code)
        ]

    def test_documents_quote_every_command(self) -> None:
        # страховка от пустой проверки: разбор нашёл блоки, и каждая команда
        # калькулятора показана в документах хотя бы раз
        self.assertGreaterEqual(len(self.blocks), 8)
        quoted = {
            shlex.split(command)[2]
            for block in self.blocks
            for command in block.commands
        }
        self.assertEqual(set(COMMANDS), quoted)

    def test_block_holds_only_calculator_calls(self) -> None:
        for block in self.blocks:
            for command in block.commands:
                with self.subTest(block=f"{block.path}:{block.line}", command=command):
                    self.assertTrue(command.startswith(PREFIX + " "), command)

    def test_block_commands_run(self) -> None:
        for block in self.blocks:
            for command in block.commands:
                result = run(command)
                with self.subTest(block=f"{block.path}:{block.line}", command=command):
                    self.assertEqual(
                        0, result.returncode, result.stdout + result.stderr
                    )

    def test_every_block_shows_its_output(self) -> None:
        for block in self.blocks:
            with self.subTest(block=f"{block.path}:{block.line}"):
                self.assertIsNotNone(
                    block.expected,
                    "за блоком команд должен идти блок ```text с их выводом",
                )

    def test_shown_output_matches(self) -> None:
        for block in self.blocks:
            if block.expected is None:
                continue
            actual = shown_output(block)
            with self.subTest(block=f"{block.path}:{block.line}"):
                self.assertEqual(
                    actual,
                    "\n".join(block.expected),
                    f"вывод в {block.path}:{block.expected_line} расходится с "
                    "фактическим",
                )

    def test_inline_commands_run(self) -> None:
        for path, line, code in self.inline:
            if PLACEHOLDER.search(code):
                continue
            result = run(code)
            with self.subTest(place=f"{path}:{line}", command=code):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_fragments_name_existing_commands_and_flags(self) -> None:
        for path, line, code in self.fragments:
            match = FRAGMENT.search(code)
            assert match is not None  # отобрано по FRAGMENT в setUpClass
            command = match.group("command")
            with self.subTest(place=f"{path}:{line}", fragment=code):
                if command is None:
                    self.assertTrue((SKILL / "scripts" / "eval_calc.py").is_file())
                    continue
                self.assertIn(command, COMMANDS)
                result = run(f"{PREFIX} {command} --help")
                self.assertEqual(0, result.returncode, result.stderr)
                for flag in FLAG.findall(match.group("rest")):
                    exact = rf"(?<![\w-]){re.escape(flag)}(?![\w-])"
                    self.assertRegex(result.stdout, exact)


class ParsingTest(unittest.TestCase):
    """Правила разбора, на которых держится DocCommandsTest."""

    DOCUMENT = "\n".join(
        [
            "Текст.",
            "",
            "```bash",
            "# комментарий",
            f"{PREFIX} noise 0.8 0.81 0.82",
            "```",
            "",
            "```text",
            "вывод",
            "```",
            "",
            "```bash",
            f"{PREFIX} passk --p 0.5 --k 2",
            "```",
            "Абзац между блоками.",
            "```text",
            "не вывод этого блока",
            "```",
        ]
    )

    def test_output_block_must_follow_directly(self) -> None:
        first, second = command_blocks_in(self.DOCUMENT, "doc.md")

        self.assertEqual([f"{PREFIX} noise 0.8 0.81 0.82"], first.commands)
        self.assertEqual(["вывод"], first.expected)
        self.assertEqual(8, first.expected_line)
        self.assertIsNone(second.expected)

    def test_fragments_and_placeholders(self) -> None:
        match = FRAGMENT.search("eval_calc.py compare --only-a 2")
        assert match is not None
        self.assertEqual("compare", match.group("command"))
        self.assertEqual(["--only-a"], FLAG.findall(match.group("rest")))
        self.assertTrue(PLACEHOLDER.search(f"{PREFIX} noise <доли прогонов>"))
        self.assertIsNone(PLACEHOLDER.search(f"{PREFIX} noise 0.8 0.81 0.82"))


if __name__ == "__main__":
    unittest.main()
