"""Генератор блоков вывода калькулятора в документах скилла."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


class CommandLineTests(unittest.TestCase):
    def main(self, *arguments: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return tool.main(list(arguments))

    def test_skill_documents_are_up_to_date(self) -> None:
        self.assertEqual(0, self.main("--check"))

    def test_check_reports_stale_document_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "doc.md"
            stale = (
                f"```bash\n{PREFIX} passk --p 0.5 --k 2\n```\n\n```text\nстарый\n```\n"
            )
            path.write_text(stale, encoding="utf-8")

            self.assertEqual(1, self.main("--check", str(path)))
            self.assertEqual(stale, path.read_text(encoding="utf-8"))
            self.assertEqual(0, self.main(str(path)))
            self.assertIn("**Pass@2**: 0.75000", path.read_text(encoding="utf-8"))
            self.assertEqual(0, self.main("--check", str(path)))


if __name__ == "__main__":
    unittest.main()
