"""Генератор блоков вывода калькулятора в документах скилла."""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = ROOT / ".tmp" / "tests"
sys.path.insert(0, str(ROOT / "scripts"))

import update_calc_docs as tool

PREFIX = "python3 scripts/eval_calc.py"


def fake_run(command: str) -> str:
    """Вывод-заглушка: по нему видно, какая команда запускалась."""
    return f"вывод[{command.removeprefix(PREFIX + ' ')}]\n"


class UpdateTextTests(unittest.TestCase):
    def test_stale_output_is_replaced(self) -> None:
        text = f"До.\n\n```bash\n{PREFIX} noise 1 2 3\n```\n\n```text\nстарый\nвывод\n```\n\nПосле.\n"

        updated = tool.update_text(text, fake_run)

        self.assertEqual(
            f"До.\n\n```bash\n{PREFIX} noise 1 2 3\n```\n\n"
            "```text\nвывод[noise 1 2 3]\n```\n\nПосле.\n",
            updated,
        )

    def test_marker_is_expanded(self) -> None:
        text = "Текст:\n\n<<CALC passk --p 0.5 --k 2>>\n\nДальше.\n"

        updated = tool.update_text(text, fake_run)

        self.assertEqual(
            f"Текст:\n\n```bash\n{PREFIX} passk --p 0.5 --k 2\n```\n\n"
            "```text\nвывод[passk --p 0.5 --k 2]\n```\n\nДальше.\n",
            updated,
        )

    def test_missing_output_block_is_inserted(self) -> None:
        text = f"```bash\n{PREFIX} interval --successes 1 --total 2\n```\n\nАбзац.\n"

        updated = tool.update_text(text, fake_run)

        self.assertEqual(
            f"```bash\n{PREFIX} interval --successes 1 --total 2\n```\n\n"
            "```text\nвывод[interval --successes 1 --total 2]\n```\n\nАбзац.\n",
            updated,
        )

    def test_several_commands_share_one_output_block(self) -> None:
        text = (
            f"```bash\n# два расчёта\n{PREFIX} a\n{PREFIX} b\n```\n\n```text\nx\n```\n"
        )

        updated = tool.update_text(text, fake_run)

        self.assertIn("```text\nвывод[a]\n\nвывод[b]\n```", updated)

    def test_update_is_idempotent_and_leaves_other_blocks(self) -> None:
        text = (
            "```markdown\nшаблон scripts/eval_calc.py noise\n```\n\n"
            f"```bash\n{PREFIX} noise 1 2 3\n```\n\n```text\nстарый\n```\n"
        )

        once = tool.update_text(text, fake_run)

        self.assertEqual(once, tool.update_text(once, fake_run))
        self.assertTrue(once.startswith("```markdown\nшаблон scripts/eval_calc.py"))

    def test_marker_inside_a_fence_is_left_alone(self) -> None:
        # маркер в блоке шаблона — пример синтаксиса, а не вставка: развернуть
        # его значило бы вложить ```bash в ```markdown и сломать документ
        text = "```markdown\n<<CALC noise 1 2 3>>\n```\n"

        self.assertEqual(text, tool.update_text(text, fake_run))

    def test_indented_marker_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "отступ"):
            tool.update_text("- пункт:\n\n  <<CALC noise 1 2 3>>\n", fake_run)


class CommandLineTests(unittest.TestCase):
    def main(self, *arguments: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return tool.main(list(arguments))

    def temporary_document(self, text: str) -> Path:
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "doc.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_failing_command_gives_a_message_not_a_traceback(self) -> None:
        path = self.temporary_document(f"```bash\n{PREFIX} passk --p 2 --k 1\n```\n")
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            code = self.main(str(path))

        self.assertEqual(2, code)
        self.assertIn("ошибка", errors.getvalue())
        self.assertIn("--p", errors.getvalue())

    def test_runs_without_docstrings(self) -> None:
        # python3 -OO убирает __doc__; описание для argparse не должно на нём держаться
        result = subprocess.run(
            [
                sys.executable,
                "-OO",
                str(ROOT / "scripts" / "update_calc_docs.py"),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_skill_documents_are_up_to_date(self) -> None:
        self.assertEqual(0, self.main("--check"))

    def test_check_reports_stale_document_without_writing(self) -> None:
        stale = f"```bash\n{PREFIX} passk --p 0.5 --k 2\n```\n\n```text\nстарый\n```\n"
        path = self.temporary_document(stale)

        self.assertEqual(1, self.main("--check", str(path)))
        self.assertEqual(stale, path.read_text(encoding="utf-8"))
        self.assertEqual(0, self.main(str(path)))
        self.assertIn("**Pass@2**: 0.75000", path.read_text(encoding="utf-8"))
        self.assertEqual(0, self.main("--check", str(path)))


if __name__ == "__main__":
    unittest.main()
