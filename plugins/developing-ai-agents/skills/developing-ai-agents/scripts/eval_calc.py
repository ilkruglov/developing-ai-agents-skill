#!/usr/bin/env python3
"""Калькулятор статистики оценки агента по главе 7 книги.

Числа, от которых зависит вывод оценки, считает этот скрипт, а не модель в
уме: Pass@k и Pass^k, интервал для доли успеха, объём выборки, парное
сравнение двух конфигураций, границу шума повторных прогонов и обратную
задачу — какая доля успеха попытки нужна для целевого Pass^k или Pass@k.

Каждый результат печатается с формулой, входными данными, числом и якорем на
заголовок раздела книги (`references/source-book/chapter7.md:<строка>`).
Формулы, которых в книге нет, помечены «(вывод)» с объяснением, из чего они
получены. Ошибка ввода завершает команду с кодом 2 и сообщением на русском.

Только стандартная библиотека, Python 3.10+. Запуск из каталога скилла:

    python3 scripts/eval_calc.py passk --p 0.6 --k 5
    python3 scripts/eval_calc.py passk --successes 8 --total 10 --k 2
    python3 scripts/eval_calc.py required-p --pass-hat 0.95 --k 4
    python3 scripts/eval_calc.py required-p --pass-at 0.99 --k 5
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

# Меньшая полуширина даёт n порядка 10⁸ и больше, а δ² при δ около 1e-170
# обращается в ноль; такой запрос — ошибка ввода, а не план эксперимента.
MIN_HALF_WIDTH = 1e-4
# Точный перебор по расхождениям: 200 000 — около 3 s; дальше отказ.
MAX_DISCORDANT = 200_000
# Доли ближе к 0 или 1, чем TINY, печатаются без округления до 0 или 1.
TINY = 1e-4

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
    if not MIN_HALF_WIDTH <= half_width < 1.0:
        raise InputError(
            f"--half-width должно быть в [{MIN_HALF_WIDTH}; 1) как доля, например "
            f"0.05 для ±5 п.п.; получено {half_width}"
        )


def _require_inner_probability(value: float, name: str) -> None:
    _require_probability(value, name)
    if value in (0.0, 1.0):
        raise InputError(
            f"{name} = {value}: у краёв p(1 − p) = 0 и формула даёт n = 0; "
            "нормальное приближение здесь не работает, задайте ожидаемую долю "
            "внутри (0; 1)"
        )


# --- доли у краёв ------------------------------------------------------------


def _ln(value: float) -> float:
    return math.log(value) if value > 0.0 else -math.inf


def _ln_one_minus(value: float) -> float:
    """ln(1 − x) без вычитания: точен и при x около 0."""
    return math.log1p(-value) if value < 1.0 else -math.inf


def _ln_one_minus_exp(ln_value: float) -> float:
    """ln(1 − eˣ) при x ≤ 0 без потери точности у обоих краёв."""
    if ln_value == 0.0:
        return -math.inf
    if ln_value == -math.inf:
        return 0.0
    if ln_value > -math.log(2.0):
        return math.log(-math.expm1(ln_value))
    return math.log1p(-math.exp(ln_value))


@dataclass(frozen=True)
class Share:
    """Доля через логарифмы её самой и дополнения до 1.

    1 − (1 − p)^k при (1 − p)^k < 1e-16 в float становится ровно 1, а p^k
    при k·ln p < −745 — ровно 0: печать показала бы гарантированный успех или
    невозможность. Share хранит обе стороны, и меньшая из них считается прямо,
    а не как разность с единицей.
    """

    ln_value: float
    ln_rest: float

    @classmethod
    def of(cls, value: float) -> Share:
        return cls(_ln(value), _ln_one_minus(value))

    @classmethod
    def from_ln_value(cls, ln_value: float) -> Share:
        return cls(ln_value, _ln_one_minus_exp(ln_value))

    @classmethod
    def from_ln_rest(cls, ln_rest: float) -> Share:
        return cls(_ln_one_minus_exp(ln_rest), ln_rest)

    def complement(self) -> Share:
        return Share(self.ln_rest, self.ln_value)


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


def pass_at_share(p: float, k: int) -> Share:
    """Pass@k с хвостом (1 − p)^k, посчитанным напрямую."""
    _require_probability(p, "--p")
    _require_count(k, "--k", 1)
    return Share.from_ln_rest(k * _ln_one_minus(p))


def pass_hat_share(p: float, k: int) -> Share:
    """Pass^k через k · ln p: не обращается в 0 при p^k < 1e-308."""
    _require_probability(p, "--p")
    _require_count(k, "--k", 1)
    return Share.from_ln_value(k * _ln(p))


def required_p_for_pass_hat(target: float, k: int) -> float:
    """p, при которой Pass^k = T: p = T^(1/k) — обращение p^k."""
    _require_probability(target, "--pass-hat")
    _require_count(k, "--k", 1)
    return target ** (1.0 / k)


def required_p_for_pass_at(target: float, k: int) -> float:
    """p, при которой Pass@k = T: p = 1 − (1 − T)^(1/k) — обращение 1 − (1 − p)^k."""
    _require_probability(target, "--pass-at")
    _require_count(k, "--k", 1)
    return 1.0 - (1.0 - target) ** (1.0 / k)


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
    # у краёв граница равна 0 или 1 точно; float даёт 0.9999999999999999
    low = 0.0 if successes == 0 else max(0.0, centre - spread)
    high = 1.0 if successes == total else min(1.0, centre + spread)
    return (low, high)


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
    """Точный двусторонний биномиальный тест при вероятности 0.5.

    Хвост C(n, 0) + … + C(n, m) считается рекуррентно в целых числах:
    C(n, i + 1) = C(n, i) · (n − i) / (i + 1). Вызов math.comb на каждый член
    давал квадратичное время, и 40 500 расхождений не считались за 120 s.
    """
    if n == 0:
        return 1.0
    term = 1
    tail = 1
    for i in range(min(k, n - k)):
        term = term * (n - i) // (i + 1)
        tail += term
    return min(1.0, 2 * tail / 2**n)


def mcnemar_exact(only_a: int, only_b: int) -> float:
    """Точный критерий Мак-Немара: биномиальный тест по расхождениям."""
    _require_count(only_a, "--only-a")
    _require_count(only_b, "--only-b")
    if only_a + only_b > MAX_DISCORDANT:
        raise InputError(
            f"расхождений {only_a + only_b}, больше {MAX_DISCORDANT}: точный "
            "перебор слишком долог для калькулятора; сократите данные или "
            "используйте приближённый критерий вне калькулятора"
        )
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
    """Входное число: шесть значащих цифр, но 0.99999999 не превращается в 1."""
    shown = f"{value:.6g}"
    if float(shown) in (0.0, 1.0) and value not in (0.0, 1.0):
        return f"{value:.12g}"
    return shown


MAX_DECIMALS = 12


def _decimals(value: float, decimals: int, edges: tuple[float, ...]) -> int | None:
    """Сколько знаков нужно, чтобы округление не попало на край, которого у
    значения нет (0, 100); None — больше MAX_DECIMALS, нужен другой вид."""
    while float(f"{value:.{decimals}f}") in edges and value not in edges:
        if decimals >= MAX_DECIMALS:
            return None
        decimals += 1
    return decimals


def _fixed(value: float, decimals: int, edges: tuple[float, ...]) -> str:
    """Число с decimals знаками, а вплотную к краю — отклонение от края:
    1.11e-14 вместо 0.000000000000, «100 − 1.42e-14» вместо 100.000000000000."""
    needed = _decimals(value, decimals, edges)
    if needed is not None:
        return f"{value:.{needed}f}"
    return _from_edge(value, edges)


def _from_edge(value: float, edges: tuple[float, ...]) -> str:
    edge = min(edges, key=lambda candidate: abs(value - candidate))
    if edge == 0.0:
        return f"{value:.3g}"
    sign = "−" if value < edge else "+"
    return f"{edge:g} {sign} {abs(value - edge):.3g}"


def _pct(value: float) -> str:
    return f"{_fixed(value * 100, 2, (0.0, 100.0))}%"


def _pct_range(low: float, high: float) -> str:
    """Два конца интервала с одинаковым числом знаков: 99.9943% – 99.9998%."""
    edges = (0.0, 100.0)
    needed = [_decimals(value * 100, 2, edges) for value in (low, high)]
    if None in needed:
        # один конец вплотную к краю — оба в виде отклонения от края
        shown = [_from_edge(value * 100, edges) for value in (low, high)]
        return f"{shown[0]}% – {shown[1]}%"
    decimals = max(d for d in needed if d is not None)
    return f"{low * 100:.{decimals}f}% – {high * 100:.{decimals}f}%"


def _sci(ln_value: float) -> str:
    """Малое положительное число по его логарифму, в том числе ниже порога float."""
    value = math.exp(ln_value)
    if value >= sys.float_info.min:
        return f"{value:.3g}"
    power = ln_value / math.log(10.0)
    exponent = math.floor(power)
    mantissa = f"{10 ** (power - exponent):.3g}"
    if mantissa == "10":
        mantissa, exponent = "1", exponent + 1
    return f"{mantissa}e{exponent:+03d}"


def _as_share(value: float | Share) -> Share:
    return value if isinstance(value, Share) else Share.of(value)


def _frac(value: float | Share) -> str:
    """Доля: пять знаков, у краёв — сама малая сторона, без округления до 0 или 1."""
    share = _as_share(value)
    if share.ln_value == -math.inf:
        return "0.00000"
    if share.ln_rest == -math.inf:
        return "1.00000"
    if math.exp(share.ln_value) < TINY:
        return _sci(share.ln_value)
    if math.exp(share.ln_rest) < TINY:
        return f"1 − {_sci(share.ln_rest)}"
    return f"{math.exp(share.ln_value):.5f}"


def _share(value: float | Share) -> str:
    share = _as_share(value)
    if share.ln_value == -math.inf:
        return "0.00%"
    if share.ln_rest == -math.inf:
        return "100.00%"
    if math.exp(share.ln_value) < TINY:
        return f"< {TINY * 100:g}%"
    if math.exp(share.ln_rest) < TINY:
        return f"> {(1.0 - TINY) * 100:g}%"
    return _pct(math.exp(share.ln_value))


def _prob(value: float | Share) -> str:
    return f"{_frac(value)} ({_share(value)})"


def _pp(value: float) -> str:
    return f"{_fixed(value * 100, 2, (0.0,))} п.п."


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
                _prob(pass_at_share(p, k)),
                "Pass@k = 1 − (1 − p)^k",
                inputs,
                ANCHOR_PASS_K,
            ),
            Result(
                f"Pass^{k}",
                _prob(pass_hat_share(p, k)),
                "Pass^k = p^k",
                inputs,
                ANCHOR_PASS_K,
            ),
        ],
        PASS_K_CAVEATS,
    )


def report_required_p(metric: str, target: float, k: int) -> str:
    """Какая доля успеха попытки нужна, чтобы Pass^k или Pass@k достиг T."""
    if metric == "pass-hat":
        required_p_for_pass_hat(target, k)  # проверка ввода
        p = Share.from_ln_value(_ln(target) / k)
        name, formula, inverted = f"Pass^{k}", "p = T^(1/k)", "Pass^k = p^k"
    else:
        required_p_for_pass_at(target, k)  # проверка ввода
        p = Share.from_ln_rest(_ln_one_minus(target) / k)
        name, formula = f"Pass@{k}", "p = 1 − (1 − T)^(1/k)"
        inverted = "Pass@k = 1 − (1 − p)^k"
    return _report(
        [
            Result(
                f"Нужная доля успеха попытки p для {name} ≥ {_num(target)}",
                _prob(p),
                formula,
                f"T = {_num(target)}, k = {k}",
                ANCHOR_PASS_K,
                derivation=f"обращение формулы книги {inverted}; метрика монотонно "
                f"растёт по p, поэтому при p не ниже этой доли {name} ≥ {_num(target)}",
                notes=(f"доля неудачных попыток 1 − p = {_frac(p.complement())}",),
            )
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
                f"{_prob(p)}, 95%-границы: {_frac(low)} – {_frac(high)}",
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
                f"{_prob(pass_at_share(p, k))}, 95%-границы: "
                f"{_frac(pass_at_share(low, k))} – {_frac(pass_at_share(high, k))}",
                "Pass@k = 1 − (1 − p)^k",
                inputs,
                ANCHOR_PASS_K,
                notes=(f"вывод: {bounds}",),
            ),
            Result(
                f"Pass^{k}",
                f"{_prob(pass_hat_share(p, k))}, 95%-границы: "
                f"{_frac(pass_hat_share(low, k))} – {_frac(pass_hat_share(high, k))}",
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
                _frac(se),
                "SE(p) ≈ √(p(1 − p)/n)",
                f"p = {_num(p)}, n = {total}",
                ANCHOR_SIGNIFICANCE,
            ),
            Result(
                "95%-интервал, нормальное приближение",
                f"{_pct_range(normal_low, normal_high)} (±{_pp(z_se)})",
                "p ± 1.96 · SE",
                f"p = {_num(p)}, SE = {_num(se)}, z = {Z_95}",
                ANCHOR_SIGNIFICANCE,
                notes=(
                    (
                        "вывод: множитель 1.96 — стандартный квантиль нормального "
                        "распределения для 95%; книга приводит SE и для 70 из 100 итог "
                        "примерно ±9 п.п., но множитель не называет"
                    ),
                    f"1.96 · SE = {_num(z_se)}",
                ),
            ),
            Result(
                "95%-интервал Уилсона",
                f"{_pct_range(wilson_low, wilson_high)} "
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
    # как введено: repr — кратчайшая запись, которая читается обратно в то же
    # число; 0.5000000000000001 не сливается с 0.5, как при шести знаках
    shown_values = ", ".join(repr(value) for value in values)
    return _report(
        [
            Result(
                "Граница шума (размах)",
                f"{_pp(summary.spread)} ({_pct_range(summary.low, summary.high)})",
                "max − min по долям успеха прогонов неизменной конфигурации",
                f"прогонов = {summary.runs}: {shown_values}",
                ANCHOR_SIGNIFICANCE,
                notes=(
                    (
                        "вывод: размах как граница шума — правило шага 5 playbook "
                        "build-evals; книга просит указывать среднее и диапазон "
                        "колебаний"
                    ),
                ),
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

    required = sub.add_parser(
        "required-p",
        help="какая доля успеха попытки p нужна для целевого Pass^k или Pass@k",
    )
    required.add_argument("--pass-hat", type=float, help="целевой Pass^k, 0..1")
    required.add_argument("--pass-at", type=float, help="целевой Pass@k, 0..1")
    required.add_argument("--k", type=int, required=True, help="число попыток k ≥ 1")

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
    if command == "required-p":
        if arguments.pass_hat is not None and arguments.pass_at is not None:
            raise InputError("задайте либо --pass-hat, либо --pass-at, не оба")
        if arguments.pass_hat is not None:
            return report_required_p("pass-hat", arguments.pass_hat, arguments.k)
        if arguments.pass_at is not None:
            return report_required_p("pass-at", arguments.pass_at, arguments.k)
        raise InputError("задайте целевой --pass-hat или --pass-at")
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
