"""Команды калькулятора из документов скилла выполняются и дают показанный вывод.

Проверяются SKILL.md и references/**/*.md, кроме полного текста книги
(references/source-book/). Команды запускаются из каталога скилла, как их
запускает агент. Разбор блоков общий с генератором
scripts/update_calc_docs.py, который переписывает показанный вывод.

1. Блоки кода. Блок, где есть строка `python3 scripts/eval_calc.py …`, —
   блок команд: все его непустые строки (кроме комментариев `#`) обязаны
   быть такими командами. Каждая команда запускается; ненулевой код
   возврата — ошибка. Сразу за блоком (через пустые строки) обязан идти
   блок `text` — показанный вывод. Он сверяется с фактическим выводом
   побайтно (выводы нескольких команд блока идут подряд через пустую
   строку): документ обещает, что вывод вставлен как есть, и любое
   расхождение — либо устаревший документ, либо изменившийся расчёт.
   Устаревший вывод переписывает `python3 scripts/update_calc_docs.py`.
2. Инлайн-команды. Спан `python3 scripts/eval_calc.py …` вне блоков без
   подстановок (`<…>`, `…`) — полная команда: она запускается, сверяется
   код возврата.
3. Упоминания. Любое `eval_calc.py [команда] [флаги]` в инлайн-спане
   (в том числе в команде с подстановками) или в строке блока кода, который
   не является блоком команд или вывода (например, форма шаблона), не
   запускается, но команда обязана существовать, а флаги — быть в её
   `--help`: переименование команды или флага не пройдёт незамеченным.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import unittest
from collections.abc import Iterator
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from update_calc_docs import PREFIX, SKILL, CommandBlock, command_blocks, documents
from update_calc_docs import parse_blocks as parse_fences

COMMANDS = ("passk", "interval", "sample-size", "compare", "noise")
TIMEOUT_SECONDS = 30

INLINE = re.compile(r"(?<!`)`(?P<code>[^`\n]+)`(?!`)")
FRAGMENT = re.compile(
    r"(?<![\w/])(?:scripts/)?eval_calc\.py(?:\s+(?P<command>[a-z][\w-]*))?"
    r"(?P<rest>[^`]*)"
)
FLAG = re.compile(r"(?<![\w-])--[a-z][\w-]*")
PLACEHOLDER = re.compile(r"<[^>]+>|…|\.\.\.")


def label(path: Path) -> str:
    return path.relative_to(SKILL).as_posix()


def located_blocks() -> list[tuple[str, CommandBlock]]:
    return [
        (label(path), block)
        for path in documents()
        for block in command_blocks(path.read_text(encoding="utf-8"))
    ]


def inline_spans(text: str) -> Iterator[tuple[int, str]]:
    _, inside = parse_fences(text)
    for number, line in enumerate(text.splitlines(), 1):
        if number in inside:
            continue
        for match in INLINE.finditer(line):
            yield number, match.group("code").strip()


def mention_places(text: str) -> list[tuple[int, str]]:
    """Места, где документ ссылается на калькулятор без запуска.

    Инлайн-спаны вне блоков и строки блоков кода, кроме блоков команд и
    блоков их вывода: там упоминание — часть шаблона или пояснения.
    """
    places = [(n, code) for n, code in inline_spans(text) if FRAGMENT.search(code)]
    fences, _ = parse_fences(text)
    calculator = set()
    for block in command_blocks(text):
        calculator.add(block.line)
        if block.expected_line is not None:
            calculator.add(block.expected_line)
    for fence in fences:
        if fence.line in calculator:
            continue
        for offset, line in enumerate(fence.lines, 1):
            if FRAGMENT.search(line):
                places.append((fence.line + offset, line.strip()))
    return places


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
        cls.blocks = located_blocks()
        cls.inline = []
        cls.mentions = []
        for path in documents():
            text = path.read_text(encoding="utf-8")
            cls.inline += [
                (label(path), line, code)
                for line, code in inline_spans(text)
                if code.startswith(PREFIX)
            ]
            cls.mentions += [
                (label(path), line, code) for line, code in mention_places(text)
            ]

    def test_documents_quote_every_command(self) -> None:
        # страховка от пустой проверки: разбор нашёл блоки, и каждая команда
        # калькулятора показана в документах хотя бы раз
        self.assertGreaterEqual(len(self.blocks), 8)
        quoted = {
            shlex.split(command)[2]
            for _, block in self.blocks
            for command in block.commands
        }
        self.assertEqual(set(COMMANDS), quoted)

    def test_block_holds_only_calculator_calls(self) -> None:
        for path, block in self.blocks:
            for command in block.commands:
                with self.subTest(block=f"{path}:{block.line}", command=command):
                    self.assertTrue(command.startswith(PREFIX + " "), command)

    def test_block_commands_run(self) -> None:
        for path, block in self.blocks:
            for command in block.commands:
                result = run(command)
                with self.subTest(block=f"{path}:{block.line}", command=command):
                    self.assertEqual(
                        0, result.returncode, result.stdout + result.stderr
                    )

    def test_every_block_shows_its_output(self) -> None:
        for path, block in self.blocks:
            with self.subTest(block=f"{path}:{block.line}"):
                self.assertIsNotNone(
                    block.expected,
                    "за блоком команд должен идти блок ```text с их выводом",
                )

    def test_shown_output_matches(self) -> None:
        for path, block in self.blocks:
            if block.expected is None:
                continue
            with self.subTest(block=f"{path}:{block.line}"):
                self.assertEqual(
                    shown_output(block),
                    "\n".join(block.expected),
                    f"вывод в {path}:{block.expected_line} расходится с "
                    "фактическим; перепишите: python3 scripts/update_calc_docs.py",
                )

    def test_inline_commands_run(self) -> None:
        for path, line, code in self.inline:
            if PLACEHOLDER.search(code):
                continue
            result = run(code)
            with self.subTest(place=f"{path}:{line}", command=code):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_mentions_name_existing_commands_and_flags(self) -> None:
        self.assertTrue(self.mentions)
        for path, line, code in self.mentions:
            for match in FRAGMENT.finditer(code):
                command = match.group("command")
                with self.subTest(place=f"{path}:{line}", mention=code):
                    if command is None:
                        self.assertTrue((SKILL / "scripts" / "eval_calc.py").is_file())
                        help_command = f"{PREFIX} --help"
                    else:
                        self.assertIn(command, COMMANDS)
                        help_command = f"{PREFIX} {command} --help"
                    result = run(help_command)
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
            "",
            "```markdown",
            "Граница шума: <команда scripts/eval_calc.py noize и её вывод>",
            "```",
            "",
            f"Инлайн: `{PREFIX} noise --bogus <доли>` и `eval_calc.py compare`.",
        ]
    )

    def test_output_block_must_follow_directly(self) -> None:
        first, second = command_blocks(self.DOCUMENT)

        self.assertEqual([f"{PREFIX} noise 0.8 0.81 0.82"], first.commands)
        self.assertEqual(["вывод"], first.expected)
        self.assertEqual(8, first.expected_line)
        self.assertIsNone(second.expected)

    def test_mentions_cover_template_blocks_and_placeholder_commands(self) -> None:
        places = mention_places(self.DOCUMENT)

        self.assertIn(
            (21, "Граница шума: <команда scripts/eval_calc.py noize и её вывод>"),
            places,
        )
        self.assertIn((24, f"{PREFIX} noise --bogus <доли>"), places)
        self.assertIn((24, "eval_calc.py compare"), places)
        # блоки команд и их вывода — не упоминания, их проверяют запуском
        self.assertNotIn(5, [line for line, _ in places])

    def test_fragments_and_placeholders(self) -> None:
        match = FRAGMENT.search("eval_calc.py compare --only-a 2")
        assert match is not None
        self.assertEqual("compare", match.group("command"))
        self.assertEqual(["--only-a"], FLAG.findall(match.group("rest")))
        self.assertTrue(PLACEHOLDER.search(f"{PREFIX} noise <доли прогонов>"))
        self.assertIsNone(PLACEHOLDER.search(f"{PREFIX} noise 0.8 0.81 0.82"))


if __name__ == "__main__":
    unittest.main()
