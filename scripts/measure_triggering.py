#!/usr/bin/env python3
"""Измерить, срабатывает ли установленный skill на запросах из trigger-набора.

Скрипт запускает `claude -p` на каждом запросе из корня репозитория и смотрит,
вызвал ли Claude инструмент Skill с нужным именем. Проверяется именно
установленный плагин, а не временная копия описания: только так измерение
отражает то, что произойдёт у пользователя.

Запускать из корня репозитория — рабочий каталог определяет, какой проект
видит Claude, и запуск из чужого каталога даёт ложный ноль.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL_ID = "developing-ai-agents"
# Запрос без вызова инструментов укладывается в 30-40 с; запас нужен на
# случаи, когда Claude успевает прочитать несколько reference-файлов.
QUERY_TIMEOUT = 420


def triggered(query: str, root: Path, model: str | None) -> bool | None:
    """True — skill вызван, False — нет, None — запуск не удался."""
    command = [
        "claude",
        "-p",
        query,
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    if model:
        command += ["--model", model]

    # CLAUDECODE мешает вложенному запуску claude внутри сессии Claude Code.
    environment = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=QUERY_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None

    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") != "tool_use" or block.get("name") != "Skill":
                continue
            if SKILL_ID in str(block.get("input", {}).get("skill", "")):
                return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure skill triggering")
    parser.add_argument(
        "--eval-set",
        type=Path,
        default=Path("plugins/developing-ai-agents/evals/trigger-evals.json"),
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    arguments = parser.parse_args()

    root = Path.cwd()
    if not (root / "plugins").is_dir():
        print("Запускать из корня репозитория", file=sys.stderr)
        return 2

    queries = json.loads(arguments.eval_set.read_text(encoding="utf-8"))["queries"]
    if arguments.limit:
        queries = queries[: arguments.limit]

    with ThreadPoolExecutor(max_workers=arguments.workers) as pool:
        outcomes = list(
            pool.map(lambda q: triggered(q["query"], root, arguments.model), queries)
        )

    results = [
        {
            "id": q["id"],
            "query": q["query"],
            "should_trigger": q["should_trigger"],
            "triggered": outcome,
            "pass": outcome == q["should_trigger"],
        }
        for q, outcome in zip(queries, outcomes)
    ]

    positive = [r for r in results if r["should_trigger"]]
    negative = [r for r in results if not r["should_trigger"]]
    failed = [r for r in results if r["triggered"] is None]
    recall = sum(1 for r in positive if r["triggered"]) / max(len(positive), 1)
    false_rate = sum(1 for r in negative if r["triggered"]) / max(len(negative), 1)

    summary = {
        "total": len(results),
        "positive": len(positive),
        "negative": len(negative),
        "recall": round(recall, 3),
        "false_trigger_rate": round(false_rate, 3),
        "runs_failed": len(failed),
    }
    payload = {"summary": summary, "results": results}

    if arguments.output:
        arguments.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(f"срабатывание на целевых запросах: {recall * 100:.0f}%")
    print(f"ложные срабатывания: {false_rate * 100:.0f}%")
    if failed:
        print(f"не завершились: {len(failed)}")
    for r in results:
        if not r["pass"]:
            mark = "пропуск" if r["should_trigger"] else "ложное"
            print(f"  [{mark}] {r['id']}: {r['query'][:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
