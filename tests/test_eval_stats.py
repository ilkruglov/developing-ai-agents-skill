from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import eval_stats


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "eval_stats.py"), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class BinomialTests(unittest.TestCase):
    def test_no_discordant_pairs_gives_p_one(self) -> None:
        self.assertEqual(1.0, eval_stats.binomial_two_sided(0, 0))

    def test_even_split_is_not_significant(self) -> None:
        self.assertGreater(eval_stats.binomial_two_sided(7, 15), 0.05)

    def test_one_sided_split_is_significant(self) -> None:
        self.assertLess(eval_stats.binomial_two_sided(0, 12), 0.05)


class WilsonIntervalTests(unittest.TestCase):
    def test_interval_contains_observed_rate(self) -> None:
        low, high = eval_stats.wilson_interval(95, 105)
        self.assertLess(low, 95 / 105)
        self.assertGreater(high, 95 / 105)

    def test_interval_stays_inside_zero_one_at_the_edge(self) -> None:
        low, high = eval_stats.wilson_interval(105, 105)

        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)

    def test_smaller_sample_gives_wider_interval(self) -> None:
        narrow = eval_stats.wilson_interval(90, 100)
        wide = eval_stats.wilson_interval(9, 10)

        self.assertGreater(wide[1] - wide[0], narrow[1] - narrow[0])


class OutcomeParsingTests(unittest.TestCase):
    def test_accepts_comma_and_space_separated(self) -> None:
        self.assertEqual([1, 0, 1], eval_stats.parse_outcomes("1, 0 1"))

    def test_rejects_non_binary_outcome(self) -> None:
        with self.assertRaises(ValueError):
            eval_stats.parse_outcomes("1,2")


class CommandLineTests(unittest.TestCase):
    def test_compare_reports_no_proven_improvement_on_a_tie(self) -> None:
        result = run("compare", "--a", "1,0,1,0", "--b", "0,1,0,1")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("не доказано", result.stdout)

    def test_compare_rejects_unequal_lengths(self) -> None:
        result = run("compare", "--a", "1,0", "--b", "1")

        self.assertEqual(2, result.returncode)
        self.assertIn("парное", result.stderr)

    def test_noise_requires_three_runs(self) -> None:
        result = run("noise", "0.8", "0.82")

        self.assertEqual(2, result.returncode)
        self.assertIn("минимум три прогона", result.stderr)


if __name__ == "__main__":
    unittest.main()
