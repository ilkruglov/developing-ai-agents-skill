from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_source_lock


class BuildLockTests(unittest.TestCase):
    def test_lock_contains_known_anchor_with_heading_text(self) -> None:
        lock = build_source_lock.build_lock(ROOT)

        entry = lock["anchors"]["chapter1.md:13"]

        self.assertEqual("heading", entry["kind"])
        self.assertTrue(entry["line_text"].startswith("##"))
        self.assertEqual(64, len(entry["line_sha256"]))

    def test_lock_pins_book_commits(self) -> None:
        lock = build_source_lock.build_lock(ROOT)

        self.assertEqual(
            "c3352738f4b6fe42fe34e3cf6a79bcb424a133b8",
            lock["book"]["upstream_commit"],
        )

    def test_committed_lock_matches_generated_lock(self) -> None:
        generated = build_source_lock.build_lock(ROOT)
        committed = json.loads(
            (ROOT / build_source_lock.LOCK_RELATIVE_PATH).read_text(encoding="utf-8")
        )

        self.assertEqual(generated, committed)


if __name__ == "__main__":
    unittest.main()
