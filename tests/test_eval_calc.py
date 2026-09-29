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

    def test_required_p_for_target(self) -> None:
        # Pass^k ≥ T ⇔ p ≥ T^(1/k); Pass@k ≥ T ⇔ p ≥ 1 − (1 − T)^(1/k):
        #   Pass^6 ≥ 0.9: 0.9^(1/6) = exp(ln 0.9 / 6) = exp(−0.0175601) = 0.9825932
        #   Pass^2 ≥ 0.81: √0.81 = 0.9
        #   Pass@3 ≥ 0.936: 1 − 0.064^(1/3) = 1 − 0.4 = 0.6
        #   Pass@5 ≥ 0.99: 1 − 0.01^(1/5) = 1 − 0.3981072 = 0.6018928
        self.assertAlmostEqual(
            0.9825932, eval_calc.required_p_for_pass_hat(0.9, 6), places=7
        )
        self.assertAlmostEqual(0.9, eval_calc.required_p_for_pass_hat(0.81, 2))
        self.assertAlmostEqual(0.6, eval_calc.required_p_for_pass_at(0.936, 3))
        self.assertAlmostEqual(
            0.6018928, eval_calc.required_p_for_pass_at(0.99, 5), places=7
        )

    def test_required_p_cli(self) -> None:
        hat = run("required-p", "--pass-hat", "0.9", "--k", "6")
        at = run("required-p", "--pass-at", "0.936", "--k", "3")

        self.assertEqual(0, hat.returncode, hat.stderr)
        self.assertIn("(вывод): 0.98259 (98.26%)", hat.stdout)
        self.assertIn("p = T^(1/k)", hat.stdout)
        self.assertIn("источник: `references/source-book/chapter7.md:150`", hat.stdout)
        self.assertIn("независим", hat.stdout)
        self.assertIn("1 − p = 0.01741", hat.stdout)
        self.assertEqual(0, at.returncode, at.stderr)
        self.assertIn("(вывод): 0.60000 (60.00%)", at.stdout)
        self.assertIn("p = 1 − (1 − T)^(1/k)", at.stdout)

    def test_small_and_near_one_values_are_not_rounded_away(self) -> None:
        # p = 0.1, k = 10: Pass^10 = 1e-10, пять знаков дали бы 0.00000;
        #   Pass@10 = 1 − 0.9^10 = 0.6513216
        # p = 0.88, k = 6: Pass@6 = 1 − 0.12^6 = 1 − 2.985984e-06 = 0.999997,
        #   пять знаков дали бы 1.00000 — будто успех гарантирован
        low = run("passk", "--p", "0.1", "--k", "10").stdout
        self.assertIn("**Pass^10**: 1e-10 (< 0.01%)", low)
        self.assertIn("**Pass@10**: 0.65132 (65.13%)", low)
        high = run("passk", "--p", "0.88", "--k", "6").stdout
        self.assertIn("**Pass@6**: 1 − 2.99e-06 (> 99.99%)", high)
        self.assertIn("**Pass^6**: 0.46440 (46.44%)", high)
        self.assertNotIn("1.00000", high)

    def test_saturated_tails_are_computed_not_rounded(self) -> None:
        # Хвост считается сам, а не как 1 − значение; эталоны — Decimal, 50 знаков:
        #   p = 0.99, k = 10: 1 − Pass@10 = 0.01^10 = 1e-20;
        #     Pass^10 = 0.99^10 = 0.904382075
        #   p = 0.9, k = 20: 1 − Pass@20 = 0.1^20 = 1e-20
        #   p = 0.5, k = 60: 0.5^60 = 8.67361738e-19 — и Pass^60, и 1 − Pass@60
        #   p = 0.01, k = 200: Pass^200 = 0.01^200 = 1e-400 — ниже порога float,
        #     печатается через показатель 200 · log10 0.01 = −400;
        #     Pass@200 = 1 − 0.99^200 = 1 − 0.133979675 = 0.866020325
        #   p = 0.5, k = 2000: 1 − Pass@2000 = 0.5^2000 = 10^−602.0599913
        #     = 8.7098e-603
        cases = {
            ("0.99", "10"): [
                "**Pass@10**: 1 − 1e-20 (> 99.99%)",
                "**Pass^10**: 0.90438 (90.44%)",
            ],
            ("0.9", "20"): ["**Pass@20**: 1 − 1e-20 (> 99.99%)"],
            ("0.5", "60"): [
                "**Pass@60**: 1 − 8.67e-19 (> 99.99%)",
                "**Pass^60**: 8.67e-19 (< 0.01%)",
            ],
            ("0.01", "200"): [
                "**Pass@200**: 0.86602 (86.60%)",
                "**Pass^200**: 1e-400 (< 0.01%)",
            ],
            ("0.5", "2000"): [
                "**Pass@2000**: 1 − 8.71e-603 (> 99.99%)",
                "**Pass^2000**: 8.71e-603 (< 0.01%)",
            ],
        }
        for (p, k), lines in cases.items():
            with self.subTest(p=p, k=k):
                stdout = run("passk", "--p", p, "--k", k).stdout
                for line in lines:
                    self.assertIn(line, stdout)
                self.assertNotIn("1.00000", stdout)
                self.assertNotIn("0.00000", stdout)

    def test_saturated_bounds_from_observation(self) -> None:
        # 99/100, k = 10. Уилсон (Decimal): p ∈ [0.945512475; 0.998232613].
        #   1 − Pass@10: точка 0.01^10 = 1e-20; границы 0.054487525^10 =
        #   2.30659e-13 и 0.001767387^10 = 2.97383e-28.
        #   Pass^10: 0.945512475^10 = 0.571048; 0.998232613^10 = 0.982466
        stdout = run("passk", "--successes", "99", "--total", "100", "--k", "10").stdout
        self.assertIn(
            "**Pass@10**: 1 − 1e-20 (> 99.99%), 95%-границы: "
            "1 − 2.31e-13 – 1 − 2.97e-28",
            stdout,
        )
        self.assertIn(
            "**Pass^10**: 0.90438 (90.44%), 95%-границы: 0.57105 – 0.98247", stdout
        )
        self.assertNotIn("1.00000", stdout)

    def test_other_numbers_do_not_round_onto_an_edge(self) -> None:
        # 99999/100000: SE = √(0.99999 · 0.00001 / 1e5) = 9.99995e-6;
        #   нормальная верхняя граница 0.99999 + 1.96 · SE = 1.0000096 —
        #   выше 1, два знака дали бы «100.00%»; полуширина 0.00196 п.п.
        #   дала бы «0.00 п.п.»
        # required-p --pass-hat 0.99999999 --k 3: входное T печаталось «1»
        interval = run("interval", "--successes", "99999", "--total", "100000").stdout
        normal = next(
            line
            for line in interval.splitlines()
            if line.startswith("**95%-интервал, н")
        )
        self.assertIn("– 100.001%", normal)
        self.assertIn("(±0.002 п.п.)", normal)
        self.assertNotIn("0.00 п.п.", interval)
        # SE = 9.99995e-6: пять знаков дали бы 0.00001, для SE = 1e-7 — 0.00000
        self.assertIn("**Стандартная ошибка**: 1e-05", interval)
        required = run("required-p", "--pass-hat", "0.99999999", "--k", "3").stdout
        self.assertIn("T = 0.99999999, k = 3", required)
        self.assertIn("Pass^3 ≥ 0.99999999", required)

    def test_numbers_beyond_twelve_decimals_are_not_shown_as_zero(self) -> None:
        # noise 0.5 0.5 0.5000000000000001: размах = 2^−53 = 1.11022e-16,
        #   в п.п. 1.11022e-14; s = размах · √(1/3) = 6.40988e-17 → 6.41e-15 п.п.
        #   Двенадцать знаков дали бы «0.000000000000 п.п.»
        noise = run("noise", "0.5", "0.5", "0.5000000000000001").stdout
        self.assertIn("**Граница шума (размах)**: 1.11e-14 п.п.", noise)
        self.assertIn("**Стандартное отклонение** (вывод): 6.41e-15 п.п.", noise)
        # interval 1 / 1e15: p = 1e-15, SE = √(1e-15 · (1 − 1e-15) / 1e15) ≈ 1e-15,
        #   1.96 · SE = 1.96e-15 → нормальный интервал 1e-13% ± 1.96e-13%:
        #   от −9.6e-14% до 2.96e-13%; ни одно число не должно стать нулём
        interval = run("interval", "--successes", "1", "--total", "1000000000000000")
        self.assertEqual(0, interval.returncode, interval.stderr)
        self.assertNotIn("0.000000000000", interval.stdout)
        self.assertIn("-9.6e-14% – 2.96e-13% (±1.96e-13 п.п.)", interval.stdout)
        # Уилсон (Decimal, 60 знаков): 1.76520e-14% и 5.66508e-13%; нижнему концу
        # нужен вид с показателем, верхний печатается так же, а не 0.000000000001%
        self.assertIn("(вывод): 1.77e-14% – 5.67e-13%", interval.stdout)

    def test_interval_ends_share_the_same_precision(self) -> None:
        # 99999/100000, Уилсон (Decimal): 0.9999433514… и 0.9999982347…;
        #   верхней границе нужно 4 знака (99.9998%), нижняя печатается так же:
        #   99.9943%, а не 99.99%
        stdout = run("interval", "--successes", "99999", "--total", "100000").stdout
        self.assertIn("(вывод): 99.9943% – 99.9998% (", stdout)
        self.assertIn(
            "**95%-интервал, нормальное приближение**: 99.997% – 100.001%", stdout
        )

    def test_wilson_edges_are_exact(self) -> None:
        # при s = n верхняя граница Уилсона равна 1 точно, при s = 0 нижняя — 0:
        # (p + z²/2n + z·√(z²/4n²)) / (1 + z²/n) = (1 + z²/n) / (1 + z²/n);
        # в float 100/100 давало 0.9999999999999999 и печаталось бы «1 − 1.11e-16»
        for n in (100, 105, 12345):
            with self.subTest(n=n):
                self.assertEqual(1.0, eval_calc.wilson_interval(n, n)[1])
                self.assertEqual(0.0, eval_calc.wilson_interval(0, n)[0])

    def test_exact_edges_stay_exact(self) -> None:
        # p = 0 и p = 1 — не насыщение, а точные 0 и 1
        zero = run("passk", "--p", "0", "--k", "3").stdout
        one = run("passk", "--p", "1", "--k", "3").stdout
        self.assertIn("**Pass^3**: 0.00000 (0.00%)", zero)
        self.assertIn("**Pass@3**: 0.00000 (0.00%)", zero)
        self.assertIn("**Pass@3**: 1.00000 (100.00%)", one)
        self.assertIn("**Pass^3**: 1.00000 (100.00%)", one)

    def test_interval_percent_does_not_round_to_the_edge(self) -> None:
        # 99999/100000: Уилсон, z² = 3.8416, n = 1e5 (Decimal):
        #   верхняя граница 0.99999823…, двух знаков в процентах мало —
        #   печатается столько знаков, чтобы граница не стала 100.00%
        stdout = run("interval", "--successes", "99999", "--total", "100000").stdout
        wilson = next(
            line for line in stdout.splitlines() if line.startswith("**95%-интервал У")
        )
        self.assertNotIn("100.00%", wilson)
        self.assertRegex(wilson, r"– 99\.9998\d*%")

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

    def test_mcnemar_exact_on_large_counts(self) -> None:
        # b = 20000, c = 20500, n = 40500. Независимая сверка: сумма
        # exp(lgamma(n+1) − lgamma(i+1) − lgamma(n−i+1) − n·ln 2) по i ≤ 20000,
        # удвоенная, = 0.0131538; нормальное приближение с поправкой на
        # непрерывность: z = (500 − 1)/√40500 = 2.4796 → p = 0.0131548.
        # Раньше каждый член считался math.comb заново, и счёт не укладывался
        # в 120 s; теперь рекуррентно.
        self.assertAlmostEqual(
            0.0131538, eval_calc.mcnemar_exact(20000, 20500), places=6
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "compare",
                "--only-a",
                "20000",
                "--only-b",
                "20500",
            ],
            cwd=SKILL,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("p-value = 0.0132", result.stdout)

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
            ("required-p", "--pass-hat", "0.9", "--k", "6"),
            ("required-p", "--pass-at", "0.99", "--k", "5"),
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

    def test_non_book_steps_inside_book_results_are_noted(self) -> None:
        interval = run("interval", "--successes", "70", "--total", "100").stdout
        normal = next(
            block
            for block in interval.split("\n\n")
            if block.startswith("**95%-интервал, нормальное")
        )
        self.assertIn("- вывод: множитель 1.96", normal)
        self.assertIn("±9", normal)
        noise = run("noise", "0.784", "0.812", "0.795", "0.846", "0.803").stdout
        spread = noise.split("\n\n")[0]
        self.assertTrue(spread.startswith("**Граница шума (размах)**"), spread)
        self.assertIn("- вывод: ", spread)
        self.assertIn("build-evals", spread)
        self.assertIn("диапазон колебаний", spread)

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
            (eval_calc.sample_size, (0.7, 1e-170)),
            (eval_calc.sample_size_difference, (0.7, 0.73, 1e-170)),
            (eval_calc.required_p_for_pass_hat, (1.2, 3)),
            (eval_calc.required_p_for_pass_at, (0.9, 0)),
            (eval_calc.mcnemar_exact, (150000, 150001)),
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
            (("sample-size", "--p", "0.7", "--half-width", "1e-170"), "half-width"),
            (("required-p", "--pass-hat", "1.5", "--k", "3"), "[0; 1]"),
            (("required-p", "--k", "3"), "--pass-hat"),
            (("compare", "--only-a", "150000", "--only-b", "150001"), "200000"),
            (
                ("required-p", "--pass-hat", "0.9", "--pass-at", "0.9", "--k", "3"),
                "оба",
            ),
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
        # вывод обёртки 0.7.2 байт в байт, кроме подписи двух отклонений: 2σ
        # при пяти прогонах обычно меньше размаха (≈ 2.33σ), «консервативно»
        # вводило в заблуждение
        expected = {
            ("noise", "0.784", "0.812", "0.795", "0.846", "0.803"): (
                "прогонов: 5\nсреднее: 80.8%\nразмах: 78.4% – 84.6%\n"
                "стандартное отклонение: 2.4 п.п.\n\n"
                "граница шума: 6.2 п.п. (размах)\n"
                "два отклонения: 4.7 п.п. (для справки)\n\n"
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
