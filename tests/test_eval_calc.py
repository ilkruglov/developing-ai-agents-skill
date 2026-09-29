"""Калькулятор статистики оценки из скилла: эталоны книги и выведенные вручную.

Эталоны книги — глава 7: p = 0.6, k = 5 → Pass@5 = 0.98976, Pass^5 = 0.07776;
70 успехов из 100 → SE ≈ 0.0458, 95%-интервал ≈ ±9 п.п. Остальные эталоны
посчитаны независимо от модуля — вывод каждого записан в комментарии рядом.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "developing-ai-agents" / "skills" / "developing-ai-agents"
SCRIPT = SKILL / "scripts" / "eval_calc.py"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

import eval_calc
import eval_stats

CHAPTER7 = SKILL / "references" / "source-book" / "chapter7.md"


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=SKILL,
        check=False,
        capture_output=True,
        text=True,
    )


class BookGoldenTests(unittest.TestCase):
    """Числа, которые книга приводит сама (chapter7.md, разделы 150 и 675)."""

    def test_pass_at_k_book_example(self) -> None:
        # 1 − 0.4^5 = 1 − 0.01024 = 0.98976; книга: «≈ 99.0%»
        self.assertAlmostEqual(0.98976, eval_calc.pass_at_k(0.6, 5), places=12)

    def test_pass_hat_k_book_example(self) -> None:
        # 0.6^5 = 0.07776; книга: «≈ 7.8%»
        self.assertAlmostEqual(0.07776, eval_calc.pass_hat_k(0.6, 5), places=12)

    def test_standard_error_book_example(self) -> None:
        # √(0.7 · 0.3 / 100) = √0.0021 = 0.0458258
        self.assertAlmostEqual(0.04583, eval_calc.standard_error(70, 100), places=5)

    def test_normal_interval_book_example(self) -> None:
        # 1.96 · 0.0458258 = 0.0898185 → ±8.98 п.п.; книга: «70% ± 9 п.п.»
        low, high = eval_calc.normal_interval(70, 100)
        self.assertAlmostEqual(0.0898, (high - low) / 2, places=4)
        self.assertEqual(9, round((high - low) / 2 * 100))
        self.assertAlmostEqual(0.7, (low + high) / 2, places=12)

    def test_book_example_in_cli_output(self) -> None:
        passk = run("passk", "--p", "0.6", "--k", "5")
        interval = run("interval", "--successes", "70", "--total", "100")

        self.assertEqual(0, passk.returncode, passk.stderr)
        self.assertIn("**Pass@5**: 0.98976 (98.98%)", passk.stdout)
        self.assertIn("**Pass^5**: 0.07776 (7.78%)", passk.stdout)
        self.assertEqual(0, interval.returncode, interval.stderr)
        self.assertIn("0.04583", interval.stdout)
        self.assertIn("±8.98 п.п.", interval.stdout)


class HandDerivedGoldenTests(unittest.TestCase):
    """Параметры не из книги; ожидаемое посчитано вне модуля."""

    def test_passk_other_parameters(self) -> None:
        # p = 0.9, k = 3: Pass@3 = 1 − 0.1^3 = 0.999; Pass^3 = 0.9^3 = 0.729
        self.assertAlmostEqual(0.999, eval_calc.pass_at_k(0.9, 3), places=12)
        self.assertAlmostEqual(0.729, eval_calc.pass_hat_k(0.9, 3), places=12)

    def test_passk_edges(self) -> None:
        # k = 1: обе метрики равны p; p = 0 и p = 1 — вырожденные края
        self.assertAlmostEqual(0.37, eval_calc.pass_at_k(0.37, 1), places=12)
        self.assertAlmostEqual(0.37, eval_calc.pass_hat_k(0.37, 1), places=12)
        self.assertEqual(0.0, eval_calc.pass_at_k(0.0, 4))
        self.assertEqual(1.0, eval_calc.pass_hat_k(1.0, 4))

    def test_wilson_interval_eight_of_ten(self) -> None:
        # 8/10, z = 1.96, z² = 3.8416:
        #   знаменатель = 1 + 3.8416/10 = 1.38416
        #   центр = (0.8 + 3.8416/20) / 1.38416 = 0.99208 / 1.38416 = 0.716738
        #   разброс = 1.96 · √(0.8·0.2/10 + 3.8416/400) / 1.38416
        #           = 1.96 · √0.025604 / 1.38416 = 0.226581
        #   → [0.490157; 0.943319]
        low, high = eval_calc.wilson_interval(8, 10)
        self.assertAlmostEqual(0.490157, low, places=6)
        self.assertAlmostEqual(0.943319, high, places=6)

    def test_passk_bounds_from_observation(self) -> None:
        # 8/10, k = 2, границы p по Уилсону [0.490157; 0.943319] (см. выше);
        # метрики монотонны по p, поэтому границы переносятся:
        #   Pass@2: 1 − 0.509843² = 0.740060;  1 − 0.056681² = 0.996787
        #   Pass^2: 0.490157² = 0.240254;      0.943319² = 0.889851
        result = run("passk", "--successes", "8", "--total", "10", "--k", "2")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("**Pass@2**: 0.96000 (96.00%)", result.stdout)
        self.assertIn("95%-границы: 0.74006 – 0.99679", result.stdout)
        self.assertIn("**Pass^2**: 0.64000 (64.00%)", result.stdout)
        self.assertIn("95%-границы: 0.24025 – 0.88985", result.stdout)

    def test_interval_near_one(self) -> None:
        # 19/20: SE = √(0.95 · 0.05 / 20) = √0.002375 = 0.048734
        #   нормальное: 0.95 ± 1.96 · 0.048734 = 0.95 ± 0.095519
        #             → [0.854481; 1.045519] — верхняя граница выше 1
        #   Уилсон: знаменатель 1.19208, центр 1.04604 / 1.19208 = 0.877491,
        #           разброс 1.96 · √(0.002375 + 0.002401) / 1.19208 = 0.113627
        #         → [0.763864; 0.991119]
        low, high = eval_calc.normal_interval(19, 20)
        self.assertAlmostEqual(0.854481, low, places=6)
        self.assertAlmostEqual(1.045519, high, places=6)
        low, high = eval_calc.wilson_interval(19, 20)
        self.assertAlmostEqual(0.763864, low, places=6)
        self.assertAlmostEqual(0.991119, high, places=6)

        result = run("interval", "--successes", "19", "--total", "20")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("85.45% – 104.55%", result.stdout)
        self.assertIn("76.39% – 99.11%", result.stdout)
        self.assertIn("выходит за [0; 1]", result.stdout)

    def test_interval_all_failures(self) -> None:
        # 0/20: SE = 0, нормальный интервал схлопывается в точку [0; 0];
        # Уилсон: центр = 0.09604/1.19208 = 0.080565, разброс тот же → [0; 0.161130]
        self.assertEqual((0.0, 0.0), eval_calc.normal_interval(0, 20))
        low, high = eval_calc.wilson_interval(0, 20)
        self.assertEqual(0.0, low)
        self.assertAlmostEqual(0.161130, high, places=6)
        result = run("interval", "--successes", "0", "--total", "20")
        self.assertIn("схлопывается", result.stdout)

    def test_sample_size_single(self) -> None:
        # n = ⌈1.96² · p(1 − p) / δ²⌉:
        #   p = 0.7, δ = 0.05: 3.8416 · 0.21 / 0.0025 = 322.69 → 323
        #   p = 0.7, δ = 0.09: 3.8416 · 0.21 / 0.0081 = 99.60 → 100 (книга: 100 и ±9)
        #   p = 0.5, δ = 0.098: 3.8416 · 0.25 / 0.009604 = 100.0 ровно → 100, не 101
        self.assertEqual(323, eval_calc.sample_size(0.7, 0.05))
        self.assertEqual(100, eval_calc.sample_size(0.7, 0.09))
        self.assertEqual(100, eval_calc.sample_size(0.5, 0.098))

    def test_sample_size_difference(self) -> None:
        # n на группу = ⌈1.96² · (p₁(1 − p₁) + p₂(1 − p₂)) / δ²⌉:
        #   0.70 и 0.73, δ = 0.03: 3.8416 · (0.21 + 0.1971) / 0.0009
        #   = 1.563915 / 0.0009 = 1737.68 → 1738
        self.assertEqual(1738, eval_calc.sample_size_difference(0.7, 0.73, 0.03))
        result = run(
            "sample-size", "--p", "0.7", "--p2", "0.73", "--half-width", "0.03"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(": 1738", result.stdout)
        self.assertIn("(вывод)", result.stdout)

    def test_mcnemar_exact(self) -> None:
        # b = 2, c = 10, n = 12: 2 · (C(12,0) + C(12,1) + C(12,2)) / 2^12
        #   = 2 · (1 + 12 + 66) / 4096 = 158 / 4096 = 0.038574
        self.assertAlmostEqual(0.038574, eval_calc.mcnemar_exact(2, 10), places=6)
        # b = 1, c = 1: 2 · (1 + 2) / 4 = 1.5 → ограничено 1
        self.assertEqual(1.0, eval_calc.mcnemar_exact(1, 1))
        self.assertEqual(1.0, eval_calc.mcnemar_exact(0, 0))

    def test_compare_from_counts_is_significant(self) -> None:
        result = run("compare", "--only-a", "2", "--only-b", "10")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("p-value = 0.0386", result.stdout)
        self.assertIn("значима на уровне 0.05", result.stdout)

    def test_compare_from_vectors(self) -> None:
        # A: 1,1,0,1,0; B: 1,0,0,1,1 → только A во 2-й задаче, только B в 5-й
        self.assertEqual((1, 1), eval_calc.discordant([1, 1, 0, 1, 0], [1, 0, 0, 1, 1]))
        result = run("compare", "--a", "1,1,0,1,0", "--b", "1,0,0,1,1")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("p-value = 1.0000", result.stdout)
        self.assertIn("не доказано", result.stdout)
        self.assertIn("бюджет", result.stdout)

    def test_noise(self) -> None:
        # 0.784 0.812 0.795 0.846 0.803: сумма 4.040, среднее 0.808;
        # размах 0.846 − 0.784 = 0.062; отклонения −0.024, 0.004, −0.013,
        # 0.038, −0.005; квадраты в сумме 0.00223; /4 = 0.0005575; √ = 0.023611
        summary = eval_calc.noise_summary([0.784, 0.812, 0.795, 0.846, 0.803])
        self.assertEqual(5, summary.runs)
        self.assertAlmostEqual(0.808, summary.mean, places=12)
        self.assertAlmostEqual(0.062, summary.spread, places=12)
        self.assertAlmostEqual(0.023611, summary.stdev, places=6)
        result = run("noise", "0.784", "0.812", "0.795", "0.846", "0.803")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("6.20 п.п.", result.stdout)


class OutputContractTests(unittest.TestCase):
    """Каждый результат: формула, входы, число, якорь; вывод помечен."""

    def test_every_result_has_formula_inputs_and_anchor(self) -> None:
        commands = [
            ("passk", "--p", "0.6", "--k", "5"),
            ("passk", "--successes", "8", "--total", "10", "--k", "2"),
            ("interval", "--successes", "70", "--total", "100"),
            ("sample-size", "--p", "0.7", "--half-width", "0.05"),
            ("sample-size", "--p", "0.7", "--p2", "0.73", "--half-width", "0.03"),
            ("compare", "--only-a", "2", "--only-b", "10"),
            ("noise", "0.784", "0.812", "0.795", "0.846", "0.803"),
        ]
        for arguments in commands:
            with self.subTest(arguments=arguments):
                result = run(*arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                blocks = [
                    block
                    for block in result.stdout.split("\n\n")
                    if block.startswith("**")
                ]
                self.assertTrue(blocks, result.stdout)
                for block in blocks:
                    self.assertIn("- формула: `", block)
                    self.assertIn("- входные данные: ", block)
                    self.assertRegex(
                        block,
                        r"- источник: `references/source-book/chapter7\.md:\d+`",
                    )

    def test_non_book_formulas_are_marked(self) -> None:
        cases = {
            ("interval", "--successes", "70", "--total", "100"): "Уилсона",
            ("sample-size", "--p", "0.7", "--half-width", "0.05"): "Объём",
            ("compare", "--only-a", "2", "--only-b", "10"): "Мак-Немара",
        }
        for arguments, name in cases.items():
            with self.subTest(arguments=arguments):
                stdout = run(*arguments).stdout
                marked = [
                    line
                    for line in stdout.splitlines()
                    if line.startswith("**") and name in line
                ]
                self.assertTrue(marked, stdout)
                self.assertIn("(вывод)", marked[0])
                self.assertIn("- вывод: ", stdout)

    def test_book_formulas_are_not_marked(self) -> None:
        stdout = run("passk", "--p", "0.6", "--k", "5").stdout
        heads = [line for line in stdout.splitlines() if line.startswith("**Pass")]
        self.assertEqual(2, len(heads))
        for line in heads:
            self.assertNotIn("(вывод)", line)

    def test_passk_keeps_independence_caveat(self) -> None:
        stdout = run("passk", "--p", "0.6", "--k", "5").stdout
        self.assertIn("независим", stdout)
        self.assertIn("1 − (1 − p)^k", stdout)
        self.assertIn("p^k", stdout)

    def test_interval_shows_both_and_names_the_stable_one(self) -> None:
        stdout = run("interval", "--successes", "70", "--total", "100").stdout
        self.assertIn("нормальное приближение", stdout)
        self.assertIn("Уилсона", stdout)
        self.assertIn("у краёв", stdout)


class AnchorTests(unittest.TestCase):
    """Якоря модуля указывают на заголовки главы 7 с нужным содержанием."""

    def test_anchors_are_headings_with_the_formula(self) -> None:
        lines = CHAPTER7.read_text(encoding="utf-8").splitlines()
        expected = {
            eval_calc.ANCHOR_PASS_K: ["1-(1-p)^k", "p^k", "независимы"],
            eval_calc.ANCHOR_SIGNIFICANCE: ["SE", "Мак-Немара", "диапазон колебаний"],
        }
        for anchor, needles in expected.items():
            with self.subTest(anchor=anchor):
                path, _, number = anchor.partition(":")
                self.assertEqual("references/source-book/chapter7.md", path)
                start = int(number)
                self.assertTrue(lines[start - 1].startswith("#"), lines[start - 1])
                section = [lines[start - 1]]
                for line in lines[start:]:
                    if line.startswith("#"):
                        break
                    section.append(line)
                text = re.sub(r"\s+", "", "".join(section))
                for needle in needles:
                    self.assertIn(re.sub(r"\s+", "", needle), text)


class InputRefusalTests(unittest.TestCase):
    def test_functions_refuse_invalid_input(self) -> None:
        cases = [
            (eval_calc.pass_at_k, (1.2, 5)),
            (eval_calc.pass_at_k, (-0.1, 5)),
            (eval_calc.pass_hat_k, (0.5, 0)),
            (eval_calc.standard_error, (11, 10)),
            (eval_calc.standard_error, (1, 0)),
            (eval_calc.wilson_interval, (-1, 10)),
            (eval_calc.sample_size, (0.7, 0.0)),
            (eval_calc.sample_size, (0.0, 0.05)),
            (eval_calc.sample_size_difference, (0.7, 1.5, 0.05)),
            (eval_calc.mcnemar_exact, (-1, 3)),
            (eval_calc.discordant, ([1, 0], [1])),
            (eval_calc.discordant, ([], [])),
            (eval_calc.noise_summary, ([0.8, 0.82],)),
            (eval_calc.noise_summary, ([0.8, 0.82, 1.3],)),
        ]
        for function, arguments in cases:
            with (
                self.subTest(function=function.__name__, arguments=arguments),
                self.assertRaises(ValueError),
            ):
                function(*arguments)

    def test_cli_refuses_with_clear_message(self) -> None:
        cases = [
            (("passk", "--p", "1.5", "--k", "5"), "[0; 1]"),
            (("passk", "--p", "0.6", "--k", "0"), "k"),
            (("passk", "--successes", "11", "--total", "10", "--k", "3"), "больше"),
            (("passk", "--k", "3"), "--p"),
            (("interval", "--successes", "5", "--total", "0"), "total"),
            (("sample-size", "--p", "0.7", "--half-width", "1.5"), "half-width"),
            (("compare", "--a", "1,0", "--b", "1"), "парное"),
            (("compare", "--a", "1,2", "--b", "1,0"), "0 или 1"),
            (("compare", "--only-a", "2"), "--only-b"),
            (("noise", "0.8", "0.82"), "минимум три"),
        ]
        for arguments, fragment in cases:
            with self.subTest(arguments=arguments):
                result = run(*arguments)
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn("ошибка", result.stderr)
                self.assertIn(fragment, result.stderr)
                self.assertNotIn("Traceback", result.stderr)


class WrapperTests(unittest.TestCase):
    """Репозиторный scripts/eval_stats.py не дублирует расчёт модуля скилла."""

    def test_wrapper_reuses_skill_functions(self) -> None:
        for name in ("binomial_two_sided", "wilson_interval", "parse_outcomes"):
            with self.subTest(name=name):
                self.assertIs(getattr(eval_calc, name), getattr(eval_stats, name))

    def test_wrapper_output_is_unchanged(self) -> None:
        # вывод обёртки до переноса расчёта в скилл (0.7.2), байт в байт
        expected = {
            ("noise", "0.784", "0.812", "0.795", "0.846", "0.803"): (
                "прогонов: 5\nсреднее: 80.8%\nразмах: 78.4% – 84.6%\n"
                "стандартное отклонение: 2.4 п.п.\n\n"
                "граница шума: 6.2 п.п. (размах)\n"
                "консервативно: 4.7 п.п. (два отклонения)\n\n"
                "Разница меньше границы шума решением не является.\n"
            ),
            ("compare", "--a", "1,1,0,1,0", "--b", "1,0,0,1,1"): (
                "задач: 5\nуспех A: 3/5 = 60.0%\nуспех B: 3/5 = 60.0%\n\n"
                "расхождения: A лучше в 1, B лучше в 1\n"
                "точный тест McNemar: p = 1.000\n\n"
                "Разница не значима. Улучшение не доказано.\n"
                "Проверьте равенство бюджетов: иначе измерен бюджет, "
                "а не архитектура.\n"
            ),
            ("interval", "--successes", "95", "--total", "105"): (
                "доля успеха: 95/105 = 90.5%\n95% интервал: 83.4% – 94.7%\n"
                "полуширина: 5.7 п.п.\n\n"
                "Разница между конфигурациями меньше полуширины интервала\n"
                "не является основанием для решения.\n"
            ),
        }
        for arguments, stdout in expected.items():
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "eval_stats.py"),
                        *arguments,
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(stdout, result.stdout)


if __name__ == "__main__":
    unittest.main()
