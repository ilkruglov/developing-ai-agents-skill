#!/usr/bin/env python3
"""Статистика для сравнения прогонов агента.

Отвечает на три вопроса, которые иначе решаются на глаз: какова граница шума,
значима ли разница между конфигурациями и какой доверительный интервал у доли
успеха. Скрипт существует, чтобы этот расчёт не переписывался заново при
каждом сравнении: воспроизводимость важнее оригинальности реализации.

Только стандартная библиотека — скрипт должен работать в CI без установки
зависимостей.

Примеры:

    # граница шума по повторным прогонам неизменной конфигурации
    python3 scripts/eval_stats.py noise 0.784 0.812 0.795 0.846 0.803

    # сравнение двух конфигураций по парным исходам
    python3 scripts/eval_stats.py compare --a 1,1,0,1,0 --b 1,0,0,1,1

    # доверительный интервал доли успеха
    python3 scripts/eval_stats.py interval --successes 95 --total 105
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys

# 1.96 — квантиль нормального распределения для двустороннего интервала 95%.
# Уровень зафиксирован: подбор уровня под желаемый результат — это подгонка.
Z_95 = 1.96


def parse_outcomes(raw: str) -> list[int]:
    values = [v.strip() for v in raw.replace(" ", ",").split(",") if v.strip()]
    outcomes = []
    for value in values:
        if value not in {"0", "1"}:
            raise ValueError(f"исход должен быть 0 или 1, получено: {value}")
        outcomes.append(int(value))
    return outcomes


def binomial_two_sided(k: int, n: int) -> float:
    """Точный двусторонний биномиальный тест при p = 0.5."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(k, n - k) + 1))
    return min(1.0, 2 * tail / 2**n)


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Интервал Уилсона: устойчив у краёв шкалы, где нормальное приближение врёт."""
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denominator = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def command_noise(values: list[float]) -> int:
    if len(values) < 3:
        print("нужно минимум три прогона, иначе разброс не оценить", file=sys.stderr)
        return 2
    spread = max(values) - min(values)
    deviation = statistics.stdev(values)
    print(f"прогонов: {len(values)}")
    print(f"среднее: {statistics.mean(values) * 100:.1f}%")
    print(f"размах: {min(values) * 100:.1f}% – {max(values) * 100:.1f}%")
    print(f"стандартное отклонение: {deviation * 100:.1f} п.п.")
    print(f"\nграница шума: {spread * 100:.1f} п.п. (размах)")
    print(f"консервативно: {2 * deviation * 100:.1f} п.п. (два отклонения)")
    print("\nРазница меньше границы шума решением не является.")
    return 0


def command_compare(a: list[int], b: list[int]) -> int:
    if len(a) != len(b):
        print("наборы должны быть одинаковой длины: сравнение парное", file=sys.stderr)
        return 2

    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)
    p_value = binomial_two_sided(min(only_a, only_b), only_a + only_b)

    print(f"задач: {len(a)}")
    print(f"успех A: {sum(a)}/{len(a)} = {sum(a) / len(a) * 100:.1f}%")
    print(f"успех B: {sum(b)}/{len(b)} = {sum(b) / len(b) * 100:.1f}%")
    print(f"\nрасхождения: A лучше в {only_a}, B лучше в {only_b}")
    print(f"точный тест McNemar: p = {p_value:.3f}")

    if only_a + only_b == 0:
        print("\nКонфигурации не разошлись ни на одной задаче.")
    elif p_value > 0.05:
        print("\nРазница не значима. Улучшение не доказано.")
    else:
        print("\nРазница значима на уровне 0.05.")
    print("Проверьте равенство бюджетов: иначе измерен бюджет, а не архитектура.")
    return 0


def command_interval(successes: int, total: int) -> int:
    if successes > total:
        print("успехов не может быть больше числа задач", file=sys.stderr)
        return 2
    low, high = wilson_interval(successes, total)
    print(f"доля успеха: {successes}/{total} = {successes / total * 100:.1f}%")
    print(f"95% интервал: {low * 100:.1f}% – {high * 100:.1f}%")
    print(f"полуширина: {(high - low) / 2 * 100:.1f} п.п.")
    print("\nРазница между конфигурациями меньше полуширины интервала")
    print("не является основанием для решения.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Статистика сравнения прогонов")
    sub = parser.add_subparsers(dest="command", required=True)

    noise = sub.add_parser("noise", help="граница шума по повторным прогонам")
    noise.add_argument("values", nargs="+", type=float, help="доли успеха, 0..1")

    compare = sub.add_parser("compare", help="парное сравнение двух конфигураций")
    compare.add_argument("--a", required=True, help="исходы A: 1,0,1,...")
    compare.add_argument("--b", required=True, help="исходы B: 1,0,1,...")

    interval = sub.add_parser("interval", help="доверительный интервал доли")
    interval.add_argument("--successes", required=True, type=int)
    interval.add_argument("--total", required=True, type=int)

    arguments = parser.parse_args()

    if arguments.command == "noise":
        return command_noise(arguments.values)
    if arguments.command == "compare":
        return command_compare(parse_outcomes(arguments.a), parse_outcomes(arguments.b))
    return command_interval(arguments.successes, arguments.total)


if __name__ == "__main__":
    raise SystemExit(main())
