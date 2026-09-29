#!/usr/bin/env python3
"""Калькулятор статистики оценки агента по главе 7 книги.

Числа, от которых зависит вывод оценки, считает этот скрипт, а не модель в
уме: Pass@k и Pass^k, интервал для доли успеха, объём выборки, парное
сравнение двух конфигураций и границу шума повторных прогонов.

Каждый результат печатается с формулой, входными данными, числом и якорем на
заголовок раздела книги (`references/source-book/chapter7.md:<строка>`).
Формулы, которых в книге нет, помечены «(вывод)» с объяснением, из чего они
получены. Ошибка ввода завершает команду с кодом 2 и сообщением на русском.

Только стандартная библиотека, Python 3.10+. Запуск из каталога скилла:

    python3 scripts/eval_calc.py passk --p 0.6 --k 5
    python3 scripts/eval_calc.py passk --successes 8 --total 10 --k 2
    python3 scripts/eval_calc.py interval --successes 70 --total 100
    python3 scripts/eval_calc.py sample-size --p 0.7 --half-width 0.05
    python3 scripts/eval_calc.py sample-size --p 0.7 --p2 0.73 --half-width 0.03
    python3 scripts/eval_calc.py compare --a 1,1,0,1,0 --b 1,0,0,1,1
    python3 scripts/eval_calc.py compare --only-a 2 --only-b 10
    python3 scripts/eval_calc.py noise 0.784 0.812 0.795 0.846 0.803
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import NoReturn

# 1.96 — квантиль нормального распределения для двустороннего интервала 95%.
# Уровень зафиксирован: подбор уровня под желаемый результат — это подгонка.
Z_95 = 1.96
ALPHA = 0.05

BOOK = "references/source-book/chapter7.md"
# «### Надёжность в бизнесе: внимание к Pass^k» — обе формулы и оговорка
# о независимости попыток стоят в этом подразделе.
ANCHOR_PASS_K = f"{BOOK}:150"
# «## Статистическая значимость результатов оценки» — SE(p), пример 70 ± 9,
# парный анализ (Мак-Немар), 3–5 запусков, среднее и диапазон колебаний.
ANCHOR_SIGNIFICANCE = f"{BOOK}:675"

# Сравнение с запасом на двоичное представление: 3.8416 · 0.25 / 0.098²
# даёт 100.00000000000001, а объём должен быть ровно 100.
_CEIL_TOLERANCE = 1e-9


class InputError(ValueError):
    """Недопустимый ввод: сообщение объясняет, что исправить."""


# --- проверки входа ---------------------------------------------------------


def _require_probability(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:  # NaN тоже не проходит
        raise InputError(f"{name} должно быть в [0; 1], получено {value}")


def _require_count(value: int, name: str, minimum: int = 0) -> None:
    if value < minimum:
        raise InputError(
            f"{name} должно быть целым не меньше {minimum}, получено {value}"
        )


def _require_successes(successes: int, total: int) -> None:
    _require_count(total, "--total", 1)
    _require_count(successes, "--successes")
    if successes > total:
        raise InputError(f"--successes ({successes}) больше --total ({total})")


def _require_half_width(half_width: float) -> None:
    if not 0.0 < half_width < 1.0:
        raise InputError(
            f"--half-width должно быть в (0; 1) как доля, например 0.05 для ±5 п.п.; "
            f"получено {half_width}"
        )


def _require_inner_probability(value: float, name: str) -> None:
    _require_probability(value, name)
    if value in (0.0, 1.0):
        raise InputError(
            f"{name} = {value}: у краёв p(1 − p) = 0 и формула даёт n = 0; "
            "нормальное приближение здесь не работает, задайте ожидаемую долю "
            "внутри (0; 1)"
        )


# --- расчёт -----------------------------------------------------------------


def pass_at_k(p: float, k: int) -> float:
    """Pass@k = 1 − (1 − p)^k: хотя бы одна из k независимых попыток успешна."""
    _require_probability(p, "--p")
    _require_count(k, "--k", 1)
    return 1.0 - (1.0 - p) ** k


def pass_hat_k(p: float, k: int) -> float:
    """Pass^k = p^k: успешны все k независимых попыток."""
    _require_probability(p, "--p")
    _require_count(k, "--k", 1)
    return p**k


def standard_error(successes: int, total: int) -> float:
    """SE(p) ≈ √(p(1 − p)/n) — оценка книги."""
    _require_successes(successes, total)
    p = successes / total
    return math.sqrt(p * (1.0 - p) / total)


def normal_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """p ± z·SE без обрезки: выход за [0; 1] — признак, что приближение не работает."""
    p = successes / total if total > 0 else 0.0
    spread = z * standard_error(successes, total)
    return (p - spread, p + spread)


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Интервал Уилсона: устойчив у краёв шкалы, где нормальное приближение врёт."""
    _require_successes(successes, total)
    p = successes / total
    denominator = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def _ceil(value: float) -> int:
    return math.ceil(value - _CEIL_TOLERANCE)


def sample_size(p: float, half_width: float, z: float = Z_95) -> int:
    """n, при котором z·√(p(1 − p)/n) ≤ δ: обращение формулы SE книги."""
    _require_inner_probability(p, "--p")
    _require_half_width(half_width)
    return _ceil(z**2 * p * (1 - p) / half_width**2)


def sample_size_difference(
    p: float, p2: float, half_width: float, z: float = Z_95
) -> int:
    """n на группу, при котором полуширина 95%-интервала разности двух
    независимых долей не больше δ."""
    _require_inner_probability(p, "--p")
    _require_inner_probability(p2, "--p2")
    _require_half_width(half_width)
    return _ceil(z**2 * (p * (1 - p) + p2 * (1 - p2)) / half_width**2)


def parse_outcomes(raw: str) -> list[int]:
    """Исходы задач «1,0,1» или «1 0 1»: только 0 и 1."""
    values = [v.strip() for v in raw.replace(" ", ",").split(",") if v.strip()]
    outcomes = []
    for value in values:
        if value not in {"0", "1"}:
            raise InputError(f"исход должен быть 0 или 1, получено: {value}")
        outcomes.append(int(value))
    return outcomes


def discordant(a: Sequence[int], b: Sequence[int]) -> tuple[int, int]:
    """Число задач, где успешна только A, и где только B."""
    if len(a) != len(b):
        raise InputError(
            f"векторы --a и --b разной длины ({len(a)} и {len(b)}): "
            "сравнение парное, задачи должны совпадать"
        )
    if not a:
        raise InputError("пустые векторы --a и --b: нужна хотя бы одна задача")
    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)
    return only_a, only_b


def binomial_two_sided(k: int, n: int) -> float:
    """Точный двусторонний биномиальный тест при вероятности 0.5."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(k, n - k) + 1))
    return min(1.0, 2 * tail / 2**n)


def mcnemar_exact(only_a: int, only_b: int) -> float:
    """Точный критерий Мак-Немара: биномиальный тест по расхождениям."""
    _require_count(only_a, "--only-a")
    _require_count(only_b, "--only-b")
    return binomial_two_sided(min(only_a, only_b), only_a + only_b)


@dataclass(frozen=True)
class NoiseSummary:
    runs: int
    mean: float
    low: float
    high: float
    stdev: float

    @property
    def spread(self) -> float:
        return self.high - self.low


def noise_summary(values: Sequence[float]) -> NoiseSummary:
    """Среднее, размах и отклонение долей успеха повторных прогонов."""
    if len(values) < 3:
        raise InputError("нужно минимум три прогона, иначе разброс не оценить")
    for value in values:
        if not 0.0 <= value <= 1.0:
            raise InputError(
                f"доля успеха прогона должна быть в [0; 1], получено {value}; "
                "проценты задавайте долями: 0.784, а не 78.4"
            )
    return NoiseSummary(
        runs=len(values),
        mean=statistics.mean(values),
        low=min(values),
        high=max(values),
        stdev=statistics.stdev(values),
    )


# --- вывод ------------------------------------------------------------------


@dataclass(frozen=True)
class Result:
    """Одно число и всё, что нужно, чтобы его проверить.

    derivation не пуст, когда формулы нет в книге: заголовок получает
    пометку «(вывод)», а строка «вывод:» объясняет, откуда формула.
    """

    name: str
    shown: str
    formula: str
    inputs: str
    anchor: str
    derivation: str = ""
    notes: tuple[str, ...] = ()

    def render(self) -> str:
        mark = " (вывод)" if self.derivation else ""
        lines = [
            f"**{self.name}**{mark}: {self.shown}",
            f"- формула: `{self.formula}`",
            f"- входные данные: {self.inputs}",
        ]
        if self.derivation:
            lines.append(f"- вывод: {self.derivation}")
        lines.append(f"- источник: `{self.anchor}`")
        lines += [f"- {note}" for note in self.notes]
        return "\n".join(lines)


def _num(value: float) -> str:
    return f"{value:.6g}"


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _prob(value: float) -> str:
    return f"{value:.5f} ({_pct(value)})"


def _pp(value: float) -> str:
    return f"{value * 100:.2f} п.п."


def _p_value(value: float) -> str:
    return "< 0.0001" if value < 0.0001 else f"= {value:.4f}"


def _report(results: Sequence[Result], footer: Sequence[str] = ()) -> str:
    parts = [result.render() for result in results]
    if footer:
        parts.append("\n".join(footer))
    return "\n\n".join(parts)


PASS_K_CAVEATS = (
    "Оговорки:",
    (
        "- Формулы верны, если попытки независимы друг от друга (книга). В отчёте "
        "укажите методику: k независимых выборок одного задания или k "
        "последовательных заданий в конвейере."
    ),
    (
        "- Pass@k подходит для оценки верхней границы возможностей, Pass^k ближе к "
        "требованиям надёжности: платежи, возвраты, изменение прав доступа, "
        "развёртывание в промышленной среде (книга)."
    ),
    (
        "- Вывод, не из книги: если p различается между задачами, средний по задачам "
        "Pass^k не ниже, а Pass@k не выше расчёта по средней p (неравенство Йенсена); "
        "считайте метрики по каждой задаче."
    ),
)


def report_passk(p: float, k: int) -> str:
    inputs = f"p = {_num(p)}, k = {k}"
    return _report(
        [
            Result(
                f"Pass@{k}",
                _prob(pass_at_k(p, k)),
                "Pass@k = 1 − (1 − p)^k",
                inputs,
                ANCHOR_PASS_K,
            ),
            Result(
                f"Pass^{k}",
                _prob(pass_hat_k(p, k)),
                "Pass^k = p^k",
                inputs,
                ANCHOR_PASS_K,
            ),
        ],
        PASS_K_CAVEATS,
    )


def report_passk_observed(successes: int, total: int, k: int) -> str:
    _require_successes(successes, total)
    _require_count(k, "--k", 1)
    p = successes / total
    low, high = wilson_interval(successes, total)
    bounds = (
        "границы — та же формула в 95%-границах p по Уилсону: метрика монотонно "
        "растёт по p"
    )
    inputs = f"p = {_num(p)} ({_num(low)} – {_num(high)}), k = {k}"
    return _report(
        [
            Result(
                "Доля успеха попытки p",
                f"{_prob(p)}, 95%-границы: {low:.5f} – {high:.5f}",
                "p = успехов / попыток",
                f"успехов = {successes}, попыток = {total}",
                ANCHOR_SIGNIFICANCE,
                notes=(
                    (
                        "вывод: границы — интервал Уилсона, не формула книги; см. "
                        "команду interval"
                    ),
                ),
            ),
            Result(
                f"Pass@{k}",
                f"{_prob(pass_at_k(p, k))}, 95%-границы: "
                f"{pass_at_k(low, k):.5f} – {pass_at_k(high, k):.5f}",
                "Pass@k = 1 − (1 − p)^k",
                inputs,
                ANCHOR_PASS_K,
                notes=(f"вывод: {bounds}",),
            ),
            Result(
                f"Pass^{k}",
                f"{_prob(pass_hat_k(p, k))}, 95%-границы: "
                f"{pass_hat_k(low, k):.5f} – {pass_hat_k(high, k):.5f}",
                "Pass^k = p^k",
                inputs,
                ANCHOR_PASS_K,
                notes=(f"вывод: {bounds}",),
            ),
        ],
        PASS_K_CAVEATS,
    )


def report_interval(successes: int, total: int) -> str:
    se = standard_error(successes, total)
    p = successes / total
    normal_low, normal_high = normal_interval(successes, total)
    wilson_low, wilson_high = wilson_interval(successes, total)
    z_se = Z_95 * se
    footer = [
        (
            "Какой интервал брать: у краёв (p близко к 0 или 1, малое n) нормальное "
            "приближение ненадёжно — интервал выходит за [0; 1] или схлопывается в "
            "точку при 0/n и n/n; интервал Уилсона у краёв устойчив."
        ),
    ]
    if se == 0.0:
        footer.append(
            "Здесь нормальный интервал схлопывается в точку (SE = 0): опирайтесь "
            "на интервал Уилсона."
        )
    elif normal_low < 0.0 or normal_high > 1.0:
        footer.append(
            "Здесь нормальный интервал выходит за [0; 1]: опирайтесь на интервал "
            "Уилсона."
        )
    footer.append(
        "Для двух конфигураций на одном наборе задач книга предпочитает парный "
        "анализ (команда compare) вычитанию долей."
    )
    return _report(
        [
            Result(
                "Доля успеха",
                _prob(p),
                "p = успехов / n",
                f"успехов = {successes}, n = {total}",
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "Стандартная ошибка",
                f"{se:.5f}",
                "SE(p) ≈ √(p(1 − p)/n)",
                f"p = {_num(p)}, n = {total}",
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "95%-интервал, нормальное приближение",
                f"{_pct(normal_low)} – {_pct(normal_high)} (±{_pp(z_se)})",
                "p ± 1.96 · SE",
                f"p = {_num(p)}, SE = {_num(se)}, z = {Z_95}",
                ANCHOR_SIGNIFICANCE,
                notes=(f"1.96 · SE = {_num(z_se)}",),
            ),
            Result(
                "95%-интервал Уилсона",
                f"{_pct(wilson_low)} – {_pct(wilson_high)} "
                f"(полуширина {_pp((wilson_high - wilson_low) / 2)})",
                "(p + z²/2n ± z · √(p(1 − p)/n + z²/4n²)) / (1 + z²/n)",
                f"успехов = {successes}, n = {total}, z = {Z_95}",
                ANCHOR_SIGNIFICANCE,
                derivation="не формула книги; стандартный интервал для доли, "
                "остаётся внутри [0; 1]",
            ),
        ],
        footer,
    )


def report_sample_size(p: float, half_width: float) -> str:
    n = sample_size(p, half_width)
    return _report(
        [
            Result(
                "Объём выборки n",
                str(n),
                "n = ⌈z² · p(1 − p) / δ²⌉, z = 1.96",
                f"p = {_num(p)}, δ = {_num(half_width)}",
                ANCHOR_SIGNIFICANCE,
                derivation="обращение формулы SE книги: 1.96 · √(p(1 − p)/n) ≤ δ",
                notes=(
                    (
                        "стандартная ошибка уменьшается как 1/√n (книга): интервал "
                        "вдвое уже требует вчетверо больше задач"
                    ),
                    (
                        "p — ожидаемая доля успеха; у краёв (p близко к 0 или 1) "
                        "нормальное приближение ненадёжно"
                    ),
                ),
            )
        ]
    )


def report_sample_size_difference(p: float, p2: float, half_width: float) -> str:
    n = sample_size_difference(p, p2, half_width)
    return _report(
        [
            Result(
                "Объём выборки на группу",
                str(n),
                "n = ⌈z² · (p₁(1 − p₁) + p₂(1 − p₂)) / δ²⌉, z = 1.96",
                f"p₁ = {_num(p)}, p₂ = {_num(p2)}, δ = {_num(half_width)}",
                ANCHOR_SIGNIFICANCE,
                derivation="не формула книги; SE разности двух независимых "
                "долей √(p₁(1 − p₁)/n + p₂(1 − p₂)/n), полуширина 95%-интервала "
                "разности не больше δ",
                notes=(
                    (
                        "расчёт для двух независимых выборок; книга предпочитает "
                        "парный анализ на одном наборе задач — при положительной "
                        "корреляции исходов по задачам дисперсия разности меньше, и "
                        "этот n — оценка сверху (вывод)"
                    ),
                    (
                        "это не мощность теста: интервал ±δ исключает 0, только если "
                        "наблюдённая разница больше δ"
                    ),
                ),
            )
        ]
    )


def _compare_footer(only_a: int, only_b: int, p_value: float) -> list[str]:
    if only_a + only_b == 0:
        verdict = "Конфигурации не разошлись ни на одной задаче. Улучшение не доказано."
    elif p_value > ALPHA:
        verdict = f"Разница не значима на уровне {ALPHA}. Улучшение не доказано."
    else:
        side = "A" if only_a > only_b else "B"
        verdict = (
            f"Разница значима на уровне {ALPHA} в пользу {side}. По книге "
            "переключаться стоит, лишь когда разница ещё и превышает шум и "
            "воспроизводится."
        )
    return [
        verdict,
        "Оговорки:",
        (
            "- Бюджеты токенов, инструментов и времени у A и B должны быть равны: иначе "
            "измерен бюджет, а не архитектура."
        ),
        (
            "- Каждую конфигурацию желательно запускать с несколькими seed, например "
            "3–5 раз, указывая среднее и диапазон колебаний; одиночный запуск пригоден "
            "лишь для отбора направлений (книга)."
        ),
        (
            "- При нескольких гипотезах ужесточайте порог значимости либо независимо "
            "повторно проверяйте положительные результаты (книга)."
        ),
    ]


def report_compare(
    only_a: int,
    only_b: int,
    a: Sequence[int] | None = None,
    b: Sequence[int] | None = None,
) -> str:
    p_value = mcnemar_exact(only_a, only_b)
    if a is not None and b is not None:
        tasks = len(a)
        shown = f"только A — {only_a}, только B — {only_b} из {tasks} задач"
        inputs = (
            f"A = {sum(a)}/{tasks} ({_pct(sum(a) / tasks)}), "
            f"B = {sum(b)}/{tasks} ({_pct(sum(b) / tasks)})"
        )
    else:
        shown = f"только A — {only_a}, только B — {only_b}"
        inputs = "заданы числами расхождений"
    return _report(
        [
            Result(
                "Расхождения",
                shown,
                "b = #(A = 1, B = 0), c = #(A = 0, B = 1) на одних и тех же задачах",
                inputs,
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "Точный критерий Мак-Немара",
                f"p-value {_p_value(p_value)}",
                "p-value = min(1, 2 · Σ_{i=0..min(b, c)} C(b + c, i) / 2^(b + c))",
                f"b = {only_a}, c = {only_b}",
                ANCHOR_SIGNIFICANCE,
                derivation="книга называет критерий Мак-Немара, но не приводит "
                "формулу; точный вариант — двусторонний биномиальный тест по "
                "расхождениям при вероятности 0.5",
            ),
        ],
        _compare_footer(only_a, only_b, p_value),
    )


def report_noise(values: Sequence[float]) -> str:
    summary = noise_summary(values)
    shown_values = ", ".join(_num(value) for value in values)
    return _report(
        [
            Result(
                "Граница шума (размах)",
                f"{_pp(summary.spread)} ({_pct(summary.low)} – {_pct(summary.high)})",
                "max − min по долям успеха прогонов неизменной конфигурации",
                f"прогонов = {summary.runs}: {shown_values}",
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "Среднее",
                _prob(summary.mean),
                "Σ xᵢ / m",
                f"прогонов = {summary.runs}",
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "Стандартное отклонение",
                _pp(summary.stdev),
                "s = √(Σ (xᵢ − x̄)² / (m − 1))",
                f"среднее = {_num(summary.mean)}, прогонов = {summary.runs}",
                ANCHOR_SIGNIFICANCE,
                derivation="книга просит среднее и диапазон колебаний; отклонение "
                "— для справки",
            ),
        ],
        [
            (
                "Разница меньше границы шума решением не является. Книга: желательно "
                "3–5 запусков с разными seed; при сравнении многих вариантов порог "
                "ужесточается."
            ),
        ],
    )


# --- CLI --------------------------------------------------------------------


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"ошибка: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="eval_calc.py",
        description="Статистика оценки агента по главе 7 книги. Доли — в [0; 1].",
    )
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)

    passk = sub.add_parser(
        "passk",
        help="Pass@k и Pass^k по доле p или по наблюдению успехов/попыток",
    )
    passk.add_argument("--p", type=float, help="доля успеха одной попытки, 0..1")
    passk.add_argument("--successes", type=int, help="успешных попыток")
    passk.add_argument("--total", type=int, help="всего попыток")
    passk.add_argument("--k", type=int, required=True, help="число попыток k ≥ 1")

    interval = sub.add_parser(
        "interval", help="95%%-интервал доли: нормальное приближение и Уилсон"
    )
    interval.add_argument("--successes", type=int, required=True)
    interval.add_argument("--total", type=int, required=True)

    size = sub.add_parser(
        "sample-size", help="n для заданной полуширины 95%%-интервала (вывод)"
    )
    size.add_argument("--p", type=float, required=True, help="ожидаемая доля успеха")
    size.add_argument(
        "--p2",
        type=float,
        help="ожидаемая доля второй группы: n на группу для разности",
    )
    size.add_argument(
        "--half-width", type=float, required=True, help="полуширина δ, доля: 0.05"
    )

    compare = sub.add_parser(
        "compare", help="парное сравнение двух конфигураций, точный McNemar"
    )
    compare.add_argument("--a", help="исходы A по задачам: 1,0,1,...")
    compare.add_argument("--b", help="исходы B по тем же задачам: 1,0,1,...")
    compare.add_argument("--only-a", type=int, help="задач, где успешна только A")
    compare.add_argument("--only-b", type=int, help="задач, где успешна только B")

    noise = sub.add_parser("noise", help="граница шума по повторным прогонам")
    noise.add_argument(
        "values", nargs="+", type=float, help="доли успеха прогонов, 0..1"
    )
    return parser


def _run(arguments: argparse.Namespace) -> str:
    command = arguments.command
    if command == "passk":
        observed = arguments.successes is not None or arguments.total is not None
        if arguments.p is not None and observed:
            raise InputError("задайте либо --p, либо --successes и --total, не оба")
        if arguments.p is not None:
            return report_passk(arguments.p, arguments.k)
        if arguments.successes is None or arguments.total is None:
            raise InputError("задайте --p или пару --successes и --total")
        return report_passk_observed(arguments.successes, arguments.total, arguments.k)
    if command == "interval":
        return report_interval(arguments.successes, arguments.total)
    if command == "sample-size":
        if arguments.p2 is None:
            return report_sample_size(arguments.p, arguments.half_width)
        return report_sample_size_difference(
            arguments.p, arguments.p2, arguments.half_width
        )
    if command == "compare":
        vectors = arguments.a is not None or arguments.b is not None
        counts = arguments.only_a is not None or arguments.only_b is not None
        if vectors and counts:
            raise InputError(
                "задайте либо --a и --b, либо --only-a и --only-b, не оба способа"
            )
        if counts:
            if arguments.only_a is None or arguments.only_b is None:
                raise InputError("нужны оба числа расхождений: --only-a и --only-b")
            return report_compare(arguments.only_a, arguments.only_b)
        if arguments.a is None or arguments.b is None:
            raise InputError("задайте векторы --a и --b или числа --only-a и --only-b")
        a = parse_outcomes(arguments.a)
        b = parse_outcomes(arguments.b)
        only_a, only_b = discordant(a, b)
        return report_compare(only_a, only_b, a, b)
    return report_noise(arguments.values)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        print(_run(arguments))
    except InputError as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
