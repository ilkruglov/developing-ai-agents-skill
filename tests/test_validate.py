from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = ROOT / ".tmp" / "tests"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "validate.py"), str(root)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


@contextmanager
def repository_copy() -> Iterator[Path]:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temporary_directory:
        copied_root = Path(temporary_directory) / "repo"
        shutil.copytree(
            ROOT,
            copied_root,
            ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__"),
        )
        yield copied_root


class ValidateRepositoryTests(unittest.TestCase):
    def test_repository_validates_offline(self) -> None:
        result = run_validator(ROOT)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_rejects_non_local_book_anchor(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\nLegacy source: `book/chapter1.md:1`.\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("non-local source anchor", result.stdout)

    def test_rejects_non_local_book_anchor_in_eval_json(self) -> None:
        with repository_copy() as copied_root:
            eval_path = copied_root / "evals" / "benchmark-v2.json"
            payload = json.loads(eval_path.read_text(encoding="utf-8"))
            payload["legacy_anchor"] = "book/*.md:line"
            eval_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("non-local source anchor", result.stdout)

    def test_rejects_out_of_range_local_anchor(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\nBroken source: `references/source-book/chapter1.md:999999`.\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("source anchor out of range", result.stdout)

    def test_rejects_broken_markdown_link(self) -> None:
        with repository_copy() as copied_root:
            readme_path = copied_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8")
                + "\n[Broken local link](missing-file.md)\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("broken Markdown link", result.stdout)

    def test_rejects_missing_author_attribution(self) -> None:
        with repository_copy() as copied_root:
            readme_path = copied_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "https://github.com/bojieli",
                    "https://example.invalid/author",
                ),
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing attribution", result.stdout)

    def test_rejects_invalid_json(self) -> None:
        with repository_copy() as copied_root:
            (copied_root / "evals" / "benchmark-v2.json").write_text(
                "{\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid JSON", result.stdout)

    def test_rejects_invalid_jsonl(self) -> None:
        with repository_copy() as copied_root:
            trace_path = copied_root / "evals" / "fixtures" / "context-loop-trace.jsonl"
            trace_path.write_text("{\n", encoding="utf-8")

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid JSONL", result.stdout)

    def test_rejects_invalid_skill_frontmatter(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace(
                    "name: developing-ai-agents",
                    "name: wrong-skill-name",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid SKILL.md frontmatter", result.stdout)


if __name__ == "__main__":
    unittest.main()
