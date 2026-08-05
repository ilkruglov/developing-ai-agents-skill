from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import source_anchors


class SectionTextTests(unittest.TestCase):
    def test_section_stops_at_nested_heading(self) -> None:
        lines = [
            "## Первый раздел",
            "тело первого",
            "### Подраздел",
            "тело подраздела",
            "## Второй раздел",
            "тело второго",
        ]

        result = source_anchors.section_text(lines, 1)

        self.assertIn("тело первого", result)
        self.assertNotIn("тело подраздела", result)
        self.assertNotIn("тело второго", result)

    def test_section_stops_at_higher_level_heading(self) -> None:
        lines = ["### Подраздел", "тело", "## Раздел", "чужое тело"]

        result = source_anchors.section_text(lines, 1)

        self.assertIn("тело", result)
        self.assertNotIn("чужое тело", result)

    def test_section_for_non_heading_anchor_is_the_line_itself(self) -> None:
        lines = ["## Раздел", "первый абзац", "второй абзац"]

        result = source_anchors.section_text(lines, 2)

        self.assertEqual("первый абзац", result)

    def test_normalize_unifies_quotes_dashes_and_spaces(self) -> None:
        raw = "«контекст»  —   не   transcript"

        self.assertEqual('"контекст" - не transcript', source_anchors.normalize(raw))

    def test_anchor_key_is_stable(self) -> None:
        key = source_anchors.anchor_key("references/source-book/chapter2.md", 401)

        self.assertEqual("chapter2.md:401", key)


if __name__ == "__main__":
    unittest.main()
