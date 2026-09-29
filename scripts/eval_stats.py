#!/usr/bin/env python3
"""Статистика для сравнения прогонов агента — короткий вывод для репозитория.

Расчёт живёт в скилле: plugins/developing-ai-agents/skills/developing-ai-agents/
scripts/eval_calc.py. Этот скрипт только сохраняет прежний компактный CLI
(граница шума, парное сравнение, интервал Уилсона) и печатает те же строки,
что и до переноса; формулы, входы и якоря на книгу выводит eval_calc.py.

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
import sys
from pathlib import Path

SKILL_SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "developing-ai-agents"
    / "skills"
    / "developing-ai-agents"
    / "scripts"
)
sys.path.insert(0, str(SKILL_SCRIPTS))

# путь к модулю скилла добавлен выше, поэтому импорт стоит после кода
from eval_calc import (
    Z_95,
    binomial_two_sided,
    discordant,
    noise_summary,
    parse_outcomes,
    wilson_interval,
)

__all__ = [
    "Z_95",
    "binomial_two_sided",
    "command_compare",
    "command_interval",
    "command_noise",
    "parse_outcomes",
    "wilson_interval",
]


def command_noise(values: list[float]) -> int:
    try:
        summary = noise_summary(values)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    print(f"прогонов: {summary.runs}")
    print(f"среднее: {summary.mean * 100:.1f}%")
    print(f"размах: {summary.low * 100:.1f}% – {summary.high * 100:.1f}%")
    print(f"стандартное отклонение: {summary.stdev * 100:.1f} п.п.")
    print(f"\nграница шума: {summary.spread * 100:.1f} п.п. (размах)")
    print(f"консервативно: {2 * summary.stdev * 100:.1f} п.п. (два отклонения)")
    print("\nРазница меньше границы шума решением не является.")
    return 0


def command_compare(a: list[int], b: list[int]) -> int:
    try:
        only_a, only_b = discordant(a, b)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
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
    try:
        low, high = wilson_interval(successes, total)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
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
        try:
            a, b = parse_outcomes(arguments.a), parse_outcomes(arguments.b)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 2
        return command_compare(a, b)
    return command_interval(arguments.successes, arguments.total)


if __name__ == "__main__":
    raise SystemExit(main())
