"""Расчётный бенчмарк 0.8.0 (сценарии 401–406) согласован со своими эталонами.

Сценарий без эталона нельзя оценить по доле чисел в допуске, а сценарий со
ссылкой на отсутствующее вложение или раздел скилла нельзя честно прогнать.
Тест проверяет только структуру и связи файлов; сами эталоны выведены
независимо от калькулятора скилла (поле derivation).
"""

from __future__ import annotations

import csv
import json
import re
import unittest
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "developing-ai-agents"
SKILL = PLUGIN / "skills" / "developing-ai-agents"
BENCHMARK = PLUGIN / "evals" / "benchmark-calc-v1.json"
GOLDENS = PLUGIN / "evals" / "calc-goldens-v1.json"
EXPECTED_IDS = set(range(401, 407))
# Для каждого сценария — полный набор эталонов: имя величины → целое ли оно.
# Первая величина в списке — основная (primary): по ней считается итоговая
# доля чисел в допуске без двойного счёта производных величин.
EXPECTED_QUANTITIES: dict[int, list[tuple[str, bool]]] = {
    401: [
        ("pass_hat_6_at_p_0_88", False),
        ("required_per_attempt_success_for_pass_hat_6_0_9", False),
    ],
    402: [
        ("wilson_lower_78_of_80", False),
        ("wilson_upper_78_of_80", False),
        ("wald_half_width_1_96_se", False),
    ],
    403: [
        ("n_for_half_width_0_03_at_p_0_8", True),
        ("n_for_half_width_0_03_worst_case_p_0_5", True),
        ("tasks_to_add_to_250_at_p_0_8", True),
    ],
    404: [
        ("mcnemar_exact_two_sided_p", False),
        ("discordant_a_pass_b_fail", True),
        ("discordant_a_fail_b_pass", True),
    ],
    405: [
        ("noise_half_width_2s", False),
        ("candidate_z_in_s", False),
    ],
    406: [
        ("mcnemar_exact_two_sided_p", False),
        ("n_per_version_half_width_diff_0_05", True),
        ("tasks_to_add_to_150", True),
    ],
}
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


def exact_mcnemar(only_a: int, only_b: int) -> float:
    """Точный двусторонний McNemar, посчитанный здесь заново, без калькулятора."""
    total = only_a + only_b
    tail = sum(comb(total, i) for i in range(min(only_a, only_b) + 1))
    return float(min(Fraction(1), 2 * Fraction(tail, 2**total)))


class CalcBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.benchmark: dict = load(BENCHMARK)
        self.scenarios: list[dict] = self.benchmark["evals"]
        self.goldens: list[dict] = load(GOLDENS)["goldens"]

    def golden(self, scenario_id: int, quantity: str) -> dict:
        (match,) = [
            golden
            for golden in self.goldens
            if golden["id"] == scenario_id and golden["quantity"] == quantity
        ]
        return match

    def fixture_rows(self) -> list[dict[str, str]]:
        scenario = next(item for item in self.scenarios if item["id"] == 404)
        (attached,) = scenario["files"]
        with (PLUGIN / attached).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_benchmark_points_to_the_goldens_file(self) -> None:
        self.assertEqual(
            GOLDENS.resolve(), (PLUGIN / self.benchmark["goldens"]).resolve()
        )

    def test_each_scenario_has_exactly_the_expected_goldens(self) -> None:
        for scenario_id, expected in EXPECTED_QUANTITIES.items():
            with self.subTest(scenario=scenario_id):
                actual = [g["quantity"] for g in self.goldens if g["id"] == scenario_id]
                self.assertEqual(len(actual), len(set(actual)), "повтор величины")
                self.assertEqual({name for name, _ in expected}, set(actual))

    def test_integer_goldens_are_ints_with_zero_tolerance(self) -> None:
        for scenario_id, expected in EXPECTED_QUANTITIES.items():
            for quantity, is_integer in expected:
                with self.subTest(scenario=scenario_id, quantity=quantity):
                    golden = self.golden(scenario_id, quantity)
                    value = golden["value"]
                    if is_integer:
                        self.assertIs(type(value), int)
                        self.assertEqual(0, golden["relative_tolerance"])
                    else:
                        self.assertIs(type(value), float)
                        self.assertEqual(0.01, golden["relative_tolerance"])

    def test_exactly_one_primary_golden_per_scenario_and_it_comes_first(self) -> None:
        for scenario_id, expected in EXPECTED_QUANTITIES.items():
            with self.subTest(scenario=scenario_id):
                own = [g for g in self.goldens if g["id"] == scenario_id]
                primary = [g["quantity"] for g in own if g.get("primary") is True]
                self.assertEqual([expected[0][0]], primary)
                self.assertEqual(expected[0][0], own[0]["quantity"])

    def test_mcnemar_goldens_match_an_independent_recompute(self) -> None:
        rows = self.fixture_rows()
        only_a = sum(1 for r in rows if (r["version_a"], r["version_b"]) == ("1", "0"))
        only_b = sum(1 for r in rows if (r["version_a"], r["version_b"]) == ("0", "1"))
        self.assertAlmostEqual(
            exact_mcnemar(only_a, only_b),
            self.golden(404, "mcnemar_exact_two_sided_p")["value"],
            places=12,
        )
        prompt = next(item for item in self.scenarios if item["id"] == 406)["prompt"]
        match = re.search(r"только v1 — (\d+), только v2 — (\d+)", prompt)
        self.assertIsNotNone(match, "в запросе 406 нет чисел расхождений")
        assert match is not None
        self.assertAlmostEqual(
            exact_mcnemar(int(match.group(1)), int(match.group(2))),
            self.golden(406, "mcnemar_exact_two_sided_p")["value"],
            places=12,
        )

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

    def test_goldens_have_all_fields(self) -> None:
        for golden in self.goldens:
            with self.subTest(golden=(golden.get("id"), golden.get("quantity"))):
                self.assertLessEqual(GOLDEN_FIELDS, set(golden))
                self.assertTrue(golden["derivation"].strip())

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
        rows = self.fixture_rows()
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
