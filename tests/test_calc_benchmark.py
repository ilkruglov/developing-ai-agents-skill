"""Расчётный бенчмарк 0.8.0 (сценарии 401–406) согласован со своими эталонами.

Сценарий без эталона нельзя оценить по доле чисел в допуске, а сценарий со
ссылкой на отсутствующее вложение или раздел скилла нельзя честно прогнать.
Тест проверяет структуру и связи файлов и заново пересчитывает каждый
эталон по формулам stdlib — без калькулятора скилла, — беря входные данные
из текста запросов и из фикстуры: правка эталона, запроса или фикстуры,
меняющая число, ломает тест.
"""

from __future__ import annotations

import csv
import json
import re
import unittest
from fractions import Fraction
from math import ceil, comb, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "developing-ai-agents"
SKILL = PLUGIN / "skills" / "developing-ai-agents"
BENCHMARK = PLUGIN / "evals" / "benchmark-calc-v1.json"
GOLDENS = PLUGIN / "evals" / "calc-goldens-v1.json"
EXPECTED_IDS = set(range(401, 407))
# Для каждого сценария — полный набор эталонов: имя величины → допуск.
# Допуск 0 — целое (n, счёт задач), 0.001 — точный p McNemar (запрос требует
# точный критерий: χ² с поправкой Йейтса отличается на 0,55 % и не должен
# проходить), 0.01 — остальные дробные. Первая величина — основная (primary):
# по ней считается доля чисел в допуске без двойного счёта производных.
INTEGER, EXACT_P, FRACTION = 0, 0.001, 0.01
EXPECTED_QUANTITIES: dict[int, list[tuple[str, float]]] = {
    401: [
        ("pass_hat_6_at_p_0_88", FRACTION),
        ("required_per_attempt_success_for_pass_hat_6_0_9", FRACTION),
    ],
    402: [
        ("wilson_lower_78_of_80", FRACTION),
        ("wilson_upper_78_of_80", FRACTION),
        ("wald_half_width_1_96_se", FRACTION),
    ],
    403: [
        ("n_for_half_width_0_03_at_p_0_8", INTEGER),
        ("n_for_half_width_0_03_worst_case_p_0_5", INTEGER),
        ("tasks_to_add_to_250_at_p_0_8", INTEGER),
    ],
    404: [
        ("mcnemar_exact_two_sided_p", EXACT_P),
        ("discordant_a_pass_b_fail", INTEGER),
        ("discordant_a_fail_b_pass", INTEGER),
    ],
    405: [
        ("noise_half_width_2s", FRACTION),
        ("candidate_z_in_s", FRACTION),
    ],
    406: [
        ("mcnemar_exact_two_sided_p", EXACT_P),
        ("n_per_version_half_width_diff_0_05", INTEGER),
        ("tasks_to_add_to_150", INTEGER),
    ],
}
# Входные данные, от которых зависят эталоны, обязаны стоять в запросе
# дословно: пересчёт ниже берёт их отсюда.
PROMPT_FACTS: dict[int, list[str]] = {
    401: ["вероятностью 0,88", "ровно 6 возвратов в месяц", "не меньше чем у 90 %"],
    402: ["из 80 задач он выполнил 78", "z = 1,96", "без поправки на непрерывность"],
    403: [
        "≈ 0,8",
        "не больше 3 процентных пунктов",
        "1,96·√(p(1 − p)/n)",
        "n округляй вверх",
        "в наборе 250 задач",
    ],
    404: ["точный критерий Мак-Немара", "с четырьмя знаками после запятой"],
    405: [
        "0,713; 0,740; 0,727; 0,753; 0,720",
        "0,760 (114 из 150)",
        "среднее базы ± 2·s",
        "знаменатель n − 1",
    ],
    406: [
        "обе прошли 102 задачи, только v1 — 6, только v2 — 15, обе провалили 27",
        "не больше 5 п.п.",
        "n вверх до целого",
        "с четырьмя знаками после запятой",
    ],
}
# Сценарии, чьё третье ожидание оценивает рассуждение, которого запрос прямо
# не требует, и 405 с раскрытием риска вывода noise, — обязаны нести note.
SCENARIOS_WITH_NOTE = {402, 403, 404, 405}
Z = 1.96
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


def wilson(successes: int, total: int) -> tuple[float, float]:
    rate = successes / total
    denominator = 1 + Z * Z / total
    centre = (rate + Z * Z / (2 * total)) / denominator
    half = Z * sqrt(rate * (1 - rate) / total + Z * Z / (4 * total * total))
    return centre - half / denominator, centre + half / denominator


def ceil_n(variance: float, half_width: float) -> int:
    # round() снимает шум двоичной арифметики до ceil: 682.95…, не 683.0000001.
    return ceil(round(Z * Z * variance / half_width**2, 9))


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

    def prompt(self, scenario_id: int) -> str:
        return next(item for item in self.scenarios if item["id"] == scenario_id)[
            "prompt"
        ]

    def independent_goldens(self) -> dict[tuple[int, str], float | int]:
        """Все эталоны заново: входы — из запросов (PROMPT_FACTS) и фикстуры."""
        rows = self.fixture_rows()
        only_a = sum(1 for r in rows if (r["version_a"], r["version_b"]) == ("1", "0"))
        only_b = sum(1 for r in rows if (r["version_a"], r["version_b"]) == ("0", "1"))

        runs = [Fraction(x) for x in ("0.713", "0.740", "0.727", "0.753", "0.720")]
        mean = sum(runs) / len(runs)
        s = sqrt(sum((r - mean) ** 2 for r in runs) / (len(runs) - 1))
        candidate = Fraction(114, 150)

        match = re.search(
            r"обе прошли (\d+) задачи, только v1 — (\d+), только v2 — (\d+), "
            r"обе провалили (\d+)",
            self.prompt(406),
        )
        assert match is not None, "в запросе 406 нет таблицы исходов"
        both, v1_only, v2_only, neither = map(int, match.groups())
        tasks = both + v1_only + v2_only + neither
        p1, p2 = (both + v1_only) / tasks, (both + v2_only) / tasks
        n_diff = ceil_n(p1 * (1 - p1) + p2 * (1 - p2), 0.05)

        n_08 = ceil_n(0.8 * 0.2, 0.03)
        wilson_low, wilson_high = wilson(78, 80)
        return {
            (401, "pass_hat_6_at_p_0_88"): 0.88**6,
            (401, "required_per_attempt_success_for_pass_hat_6_0_9"): 0.9 ** (1 / 6),
            (402, "wilson_lower_78_of_80"): wilson_low,
            (402, "wilson_upper_78_of_80"): wilson_high,
            (402, "wald_half_width_1_96_se"): Z * sqrt(0.975 * 0.025 / 80),
            (403, "n_for_half_width_0_03_at_p_0_8"): n_08,
            (403, "n_for_half_width_0_03_worst_case_p_0_5"): ceil_n(0.25, 0.03),
            (403, "tasks_to_add_to_250_at_p_0_8"): n_08 - 250,
            (404, "mcnemar_exact_two_sided_p"): exact_mcnemar(only_a, only_b),
            (404, "discordant_a_pass_b_fail"): only_a,
            (404, "discordant_a_fail_b_pass"): only_b,
            (405, "noise_half_width_2s"): 2 * s,
            (405, "candidate_z_in_s"): float(candidate - mean) / s,
            (406, "mcnemar_exact_two_sided_p"): exact_mcnemar(v1_only, v2_only),
            (406, "n_per_version_half_width_diff_0_05"): n_diff,
            (406, "tasks_to_add_to_150"): n_diff - tasks,
        }

    def test_prompts_state_the_inputs_the_goldens_use(self) -> None:
        for scenario_id, facts in PROMPT_FACTS.items():
            for fact in facts:
                with self.subTest(scenario=scenario_id, fact=fact):
                    self.assertIn(fact, self.prompt(scenario_id))

    def test_every_golden_matches_an_independent_recompute(self) -> None:
        expected = self.independent_goldens()
        actual = {(g["id"], g["quantity"]): g["value"] for g in self.goldens}
        self.assertEqual(set(expected), set(actual))
        for key, value in expected.items():
            with self.subTest(golden=key):
                if isinstance(value, int):
                    self.assertEqual(value, actual[key])
                else:
                    self.assertLessEqual(abs(actual[key] - value), 1e-9 * abs(value))

    def test_fixture_has_forty_distinct_tasks(self) -> None:
        rows = self.fixture_rows()
        self.assertEqual(40, len(rows))
        self.assertEqual(40, len({row["task_id"] for row in rows}))
        for row in rows:
            with self.subTest(task=row["task_id"]):
                self.assertIn(row["version_a"], {"0", "1"})
                self.assertIn(row["version_b"], {"0", "1"})

    def test_only_the_401_inverse_golden_carries_the_disclosure_flag(self) -> None:
        flagged = [
            (g["id"], g["quantity"])
            for g in self.goldens
            if g.get("calculator_command_added_after_scenario") is True
        ]
        self.assertEqual(
            [(401, "required_per_attempt_success_for_pass_hat_6_0_9")], flagged
        )

    def test_scenarios_that_need_a_note_have_one(self) -> None:
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                note = scenario.get("note", "")
                if scenario["id"] in SCENARIOS_WITH_NOTE:
                    self.assertTrue(note.strip())
                else:
                    self.assertNotIn("note", scenario)
        note_405 = next(s for s in self.scenarios if s["id"] == 405)["note"]
        self.assertIn("noise", note_405)

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

    def test_goldens_have_the_type_and_tolerance_of_their_kind(self) -> None:
        for scenario_id, expected in EXPECTED_QUANTITIES.items():
            for quantity, tolerance in expected:
                with self.subTest(scenario=scenario_id, quantity=quantity):
                    golden = self.golden(scenario_id, quantity)
                    kind = int if tolerance == INTEGER else float
                    self.assertIs(kind, type(golden["value"]))
                    self.assertIs(type(tolerance), type(golden["relative_tolerance"]))
                    self.assertEqual(tolerance, golden["relative_tolerance"])

    def test_exactly_one_primary_golden_per_scenario_and_it_comes_first(self) -> None:
        for scenario_id, expected in EXPECTED_QUANTITIES.items():
            with self.subTest(scenario=scenario_id):
                own = [g for g in self.goldens if g["id"] == scenario_id]
                primary = [g["quantity"] for g in own if g.get("primary") is True]
                self.assertEqual([expected[0][0]], primary)
                self.assertEqual(expected[0][0], own[0]["quantity"])

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
