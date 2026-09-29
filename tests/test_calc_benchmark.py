"""Расчётный бенчмарк 0.8.0 (сценарии 401–406) согласован со своими эталонами.

Сценарий без эталона нельзя оценить по доле чисел в допуске, а сценарий со
ссылкой на отсутствующее вложение или раздел скилла нельзя честно прогнать.
Тест проверяет только структуру и связи файлов; сами эталоны выведены
независимо от калькулятора скилла (поле derivation).
"""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "developing-ai-agents"
SKILL = PLUGIN / "skills" / "developing-ai-agents"
BENCHMARK = PLUGIN / "evals" / "benchmark-calc-v1.json"
GOLDENS = PLUGIN / "evals" / "calc-goldens-v1.json"
EXPECTED_IDS = set(range(401, 407))
GOLDEN_FIELDS = {
    "id",
    "quantity",
    "value",
    "unit",
    "relative_tolerance",
    "derivation",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CalcBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios: list[dict] = load(BENCHMARK)["evals"]
        self.goldens: list[dict] = load(GOLDENS)["goldens"]

    def test_scenario_ids_are_401_to_406(self) -> None:
        ids = [scenario["id"] for scenario in self.scenarios]
        self.assertEqual(len(ids), len(set(ids)), "повторяющиеся id")
        self.assertEqual(EXPECTED_IDS, set(ids))

    def test_every_scenario_has_a_golden(self) -> None:
        golden_ids = {golden["id"] for golden in self.goldens}
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertIn(scenario["id"], golden_ids)
        self.assertLessEqual(golden_ids, EXPECTED_IDS, "эталон без сценария")

    def test_goldens_are_complete_and_tolerances_follow_the_rule(self) -> None:
        for golden in self.goldens:
            with self.subTest(golden=(golden.get("id"), golden.get("quantity"))):
                self.assertLessEqual(GOLDEN_FIELDS, set(golden))
                self.assertTrue(golden["derivation"].strip())
                value = golden["value"]
                if isinstance(value, int):
                    self.assertEqual(0, golden["relative_tolerance"])
                else:
                    self.assertIsInstance(value, float)
                    self.assertEqual(0.01, golden["relative_tolerance"])

    def test_each_scenario_has_three_expectations(self) -> None:
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                expectations = scenario["expectations"]
                self.assertEqual(3, len(expectations))
                for expectation in expectations:
                    self.assertTrue(expectation.strip())

    def test_attached_files_and_covered_references_exist(self) -> None:
        for scenario in self.scenarios:
            for attached in scenario["files"]:
                with self.subTest(scenario=scenario["id"], file=attached):
                    self.assertTrue((PLUGIN / attached).is_file())
            self.assertTrue(scenario["covers"])
            for target in scenario["covers"]:
                with self.subTest(scenario=scenario["id"], covers=target):
                    self.assertTrue((SKILL / target).is_file())

    def test_paired_fixture_matches_the_discordant_goldens(self) -> None:
        scenario = next(item for item in self.scenarios if item["id"] == 404)
        (attached,) = scenario["files"]
        with (PLUGIN / attached).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        a_only = sum(
            1 for row in rows if (row["version_a"], row["version_b"]) == ("1", "0")
        )
        b_only = sum(
            1 for row in rows if (row["version_a"], row["version_b"]) == ("0", "1")
        )
        values = {
            golden["quantity"]: golden["value"]
            for golden in self.goldens
            if golden["id"] == 404
        }
        self.assertEqual(values["discordant_a_pass_b_fail"], a_only)
        self.assertEqual(values["discordant_a_fail_b_pass"], b_only)


if __name__ == "__main__":
    unittest.main()
