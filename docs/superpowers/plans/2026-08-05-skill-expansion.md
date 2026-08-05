# Skill Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Довести skill `developing-ai-agents` до полного инженерного справочника: 12 глубоких конспектов глав, 16 паттернов, 7 playbooks, 6 шаблонов, каталог антипаттернов и расширенные evals — с машинно проверяемыми цитатами из книги.

**Architecture:** Слоистая библиотека под коротким `SKILL.md` с задачным роутером. Каждый слой отвечает на один вопрос (книга / конструкция / процедура / артефакт), файлы линкуются из `SKILL.md` напрямую (один уровень). Достоверность цитат обеспечивает трёхуровневый гейт в `scripts/validate.py`: lock якорей с sha256, требование ссылаться на заголовок, дословная цитата внутри секции якоря.

**Tech Stack:** Python 3.12 (stdlib только), unittest, ruff, Markdown. Никаких внешних зависимостей — валидатор работает offline в CI.

**Спека:** `docs/superpowers/specs/2026-08-05-skill-expansion-design.md`

## Global Constraints

Требования ниже действуют для каждой задачи плана.

- Язык контента — русский. Технические термины и идентификаторы (`Harness`, `KV-cache`, `max_steps`, `turn_id`) остаются в исходной форме.
- Книга `references/source-book/*.md` не редактируется ни при каких обстоятельствах.
- Якорь на книгу указывает только на строку-заголовок (`^#{1,6}\s`).
- Дословные цитаты обязательны только в `references/chapters/*.md`.
- Любой файл длиннее 100 строк начинается с раздела «Оглавление».
- Пути в ссылках — относительные, только прямые слэши.
- `SKILL.md` не длиннее 300 строк.
- Python: `from __future__ import annotations`, полные type hints, стиль существующего `scripts/validate.py`, форматирование `ruff format`.
- Тесты: `unittest`, изоляция через `repository_copy()` из `tests/test_validate.py`.
- Каждая задача заканчивается коммитом с explanatory-сообщением и строкой `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- После каждой задачи `python3 scripts/validate.py` и `python3 -m unittest discover -s tests` должны проходить.

## Уточнение к спеке

Спека (§10) относила `SKILL.md` к фазе 5. План меняет это: роутер наполняется **инкрементально** — каждая контентная задача сначала добавляет свою строку в роутер, получает падение валидатора «файл из роутера не существует», и только затем пишет файл. Это даёт настоящий RED-GREEN-цикл для контента и устраняет риск рассинхронизации роутера. Фаза 5 остаётся, но сводится к финальной сборке ядра `SKILL.md` и синхронизации `cheatsheet.md`, `glossary.md`, `source-map.md`.

## File Structure

**Создаются:**

| Файл | Ответственность |
|---|---|
| `scripts/source_anchors.py` | общий модуль: регексп якоря, обход документов, разбор секций, нормализация текста |
| `scripts/build_source_lock.py` | генератор `source-map.lock.json` |
| `plugins/developing-ai-agents/skills/developing-ai-agents/references/source-map.lock.json` | lock якорей: sha256 строки книги |
| `.../references/chapters/ch00…ch11.md` | 12 конспектов глав (существующие переписываются) |
| `.../references/playbooks/*.md` | 7 процедур |
| `.../references/templates/*.md` | 6 артефактов |
| `.../references/antipatterns.md` | каталог ошибок |

**Модифицируются:**

| Файл | Что меняется |
|---|---|
| `scripts/validate.py` | +5 проверок: L1 lock, L2 заголовок, L3 цитата, лимит строк `SKILL.md`, покрытие роутера |
| `tests/test_validate.py` | тесты на каждую новую проверку |
| `.../SKILL.md` | роутер, список файлов, синхронизация ядра |
| `.../references/patterns.md` | 12 → 16 паттернов, оглавление |
| `.../references/cheatsheet.md`, `glossary.md`, `source-map.md` | синхронизация с новой структурой |
| `plugins/developing-ai-agents/evals/evals.json`, `trigger-evals.json` | 26 сценариев, 20 триггер-запросов |
| `README.md`, оба `plugin.json` | версия 0.5.0, описание состава |

**Удаляется:** `.../references/chapters/index.md` (роль переходит к роутеру).

## Скелет конспекта главы

Каждый файл `references/chapters/chNN-*.md` строится по этому скелету. Задачи 7–18 ссылаются на него, не повторяя.

```markdown
# Глава N. Название

## Оглавление
- Что решает глава
- Ключевые механизмы (перечислить)
- Таблицы решений
- Failure modes
- Проверки и метрики
- Антипаттерны
- Связи

## Что решает глава
[2–3 предложения. Обязательна одна дословная цитата.]

> «дословный фрагмент» — `references/source-book/chapterN.md:LINE`

## Ключевые механизмы

### Название механизма
**Что это.** [определение]
**Зачем.** [какую проблему решает]
**Как устроен.** [структура, поля, инварианты]

> «дословный фрагмент» — `references/source-book/chapterN.md:LINE`

## Таблицы решений
[когда какой вариант выбирать; цитата не обязательна]

## Failure modes
[симптом → что его вызывает; цитата не обязательна]

## Проверки и метрики
[чем измеряется, что считается успехом]

## Антипаттерны
[ссылки на references/antipatterns.md]

## Связи
[какие patterns.md и playbooks/ опираются на главу]
```

Готовность конспекта определяется покрытием: каждая тема, отнесённая к главе в `references/source-map.md`, раскрыта как механизм с проверкой. Минимум по числу строк не задаётся.

## Скелет playbook

```markdown
# Playbook: название

## Оглавление
[разделы]

## Когда применять
[признаки запроса; когда НЕ применять]

## Что собрать до старта
[список входов: код, конфиг, traces, метрики, ограничения]

## Шаги

### Шаг 1. Название
[что сделать]
**Гейт:** не переходи к шагу 2, пока [условие].

## Выходной артефакт
[ссылка на references/templates/*.md]

## Типичные ошибки
[что идёт не так]

## Чем добрать
[ссылки на chapters/ и patterns.md]
```

## Скелет шаблона

```markdown
# Шаблон: название

## Назначение
[когда заполняется, кто потребитель]

## Обязательные поля
[список с пометкой REQUIRED; для каждого — что считается заполненным]

## Форма
[markdown-форма для копирования]

## Заполненный пример
[один реалистичный пример целиком]
```

---

## Фаза 0. Гейт

### Task 1: Общий модуль разбора якорей

**Files:**
- Create: `scripts/source_anchors.py`
- Test: `tests/test_source_anchors.py`

**Interfaces:**
- Consumes: ничего
- Produces: `LOCAL_SOURCE_ANCHOR: re.Pattern`, `HEADING: re.Pattern`, `anchor_key(path: str, start: int) -> str`, `section_text(lines: list[str], start: int) -> str`, `normalize(text: str) -> str`, `iter_skill_documents(root: Path) -> list[Path]`

- [ ] **Step 1: Написать падающий тест**

```python
from __future__ import annotations

import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import source_anchors


class SectionTextTests(unittest.TestCase):
    def test_section_stops_at_same_level_heading(self) -> None:
        lines = [
            "## Первый раздел",
            "тело первого",
            "### Подраздел",
            "тело подраздела",
            "## Второй раздел",
            "тело второго",
        ]

        result = source_anchors.section_text(lines, 1)

        self.assertIn("тело подраздела", result)
        self.assertNotIn("тело второго", result)

    def test_section_stops_at_higher_level_heading(self) -> None:
        lines = ["### Подраздел", "тело", "## Раздел", "чужое тело"]

        result = source_anchors.section_text(lines, 1)

        self.assertIn("тело", result)
        self.assertNotIn("чужое тело", result)

    def test_normalize_unifies_quotes_dashes_and_spaces(self) -> None:
        raw = "«контекст»  —   не   transcript"

        self.assertEqual('"контекст" - не transcript', source_anchors.normalize(raw))

    def test_anchor_key_is_stable(self) -> None:
        key = source_anchors.anchor_key("references/source-book/chapter2.md", 401)

        self.assertEqual("chapter2.md:401", key)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить тест, убедиться, что падает**

Run: `python3 -m unittest tests.test_source_anchors -v`
Expected: FAIL с `ModuleNotFoundError: No module named 'source_anchors'`

- [ ] **Step 3: Написать модуль**

```python
#!/usr/bin/env python3
"""Общий разбор якорей на текст книги для валидатора и генератора lock-файла."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

PLUGIN_NAME = "developing-ai-agents"
SKILL_DIRECTORY = Path("plugins") / PLUGIN_NAME / "skills" / PLUGIN_NAME
SOURCE_BOOK_DIRECTORY = SKILL_DIRECTORY / "references" / "source-book"
LOCK_RELATIVE_PATH = SKILL_DIRECTORY / "references" / "source-map.lock.json"

LOCAL_SOURCE_ANCHOR = re.compile(
    r"(?<![-\w/])(?P<path>references/source-book/[A-Za-z0-9._/-]+\.md):"
    r"(?P<start>\d+)(?:-(?P<end>\d+))?"
)
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s")

_DASHES = str.maketrans({"–": "-", "—": "-", "―": "-", "−": "-"})
_QUOTES = str.maketrans(
    {"«": '"', "»": '"', "“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"}
)


def anchor_key(path: str, start: int) -> str:
    """Ключ якоря в lock-файле: имя файла книги и номер строки."""
    return f"{Path(path).name}:{start}"


def normalize(text: str) -> str:
    """Свести типографские варианты и пробелы к сравнимому виду."""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.translate(_DASHES).translate(_QUOTES)
    return " ".join(normalized.split())


def section_text(lines: list[str], start: int) -> str:
    """Текст секции: от заголовка на строке start до следующего заголовка
    того же или более высокого уровня."""
    if start < 1 or start > len(lines):
        return ""
    heading_match = HEADING.match(lines[start - 1])
    if heading_match is None:
        return normalize(lines[start - 1])
    level = len(heading_match.group("hashes"))
    collected = [lines[start - 1]]
    for line in lines[start:]:
        match = HEADING.match(line)
        if match is not None and len(match.group("hashes")) <= level:
            break
        collected.append(line)
    return normalize(" ".join(collected))


def iter_skill_documents(root: Path) -> list[Path]:
    """Markdown-файлы скилла, кроме самого текста книги."""
    skill_root = root / SKILL_DIRECTORY
    if not skill_root.is_dir():
        return []
    documents = [
        path
        for path in sorted(skill_root.rglob("*.md"))
        if SOURCE_BOOK_DIRECTORY.name not in path.parts
    ]
    return documents
```

- [ ] **Step 4: Запустить тест, убедиться, что проходит**

Run: `python3 -m unittest tests.test_source_anchors -v`
Expected: PASS, 4 теста

- [ ] **Step 5: Проверить форматирование**

Run: `ruff format scripts/source_anchors.py tests/test_source_anchors.py && ruff check scripts tests`
Expected: без ошибок

- [ ] **Step 6: Commit**

```bash
git add scripts/source_anchors.py tests/test_source_anchors.py
git commit -m "$(cat <<'EOF'
feat: add shared source anchor parsing module

Валидатор и генератор lock-файла нуждаются в одном разборе якорей,
секций и нормализации текста. Общий модуль исключает расхождение
регекспов между двумя скриптами.

section_text ограничивает окно секцией якоря: от заголовка до следующего
заголовка того же или более высокого уровня.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Генератор lock-файла

**Files:**
- Create: `scripts/build_source_lock.py`
- Create: `plugins/developing-ai-agents/skills/developing-ai-agents/references/source-map.lock.json`
- Test: `tests/test_build_source_lock.py`

**Interfaces:**
- Consumes: `source_anchors.LOCAL_SOURCE_ANCHOR`, `anchor_key`, `HEADING`, `iter_skill_documents`
- Produces: `build_lock(root: Path) -> dict`, CLI `python3 scripts/build_source_lock.py [root]`

- [ ] **Step 1: Написать падающий тест**

```python
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_source_lock


class BuildLockTests(unittest.TestCase):
    def test_lock_contains_known_anchor_with_heading_text(self) -> None:
        lock = build_source_lock.build_lock(ROOT)

        entry = lock["anchors"]["chapter1.md:13"]

        self.assertEqual("heading", entry["kind"])
        self.assertTrue(entry["line_text"].startswith("##"))
        self.assertEqual(64, len(entry["line_sha256"]))

    def test_lock_pins_book_commits(self) -> None:
        lock = build_source_lock.build_lock(ROOT)

        self.assertEqual(
            "97de455e9aa44cf9f93441ce0c771c9aa9643d92",
            lock["book"]["upstream_commit"],
        )

    def test_committed_lock_matches_generated_lock(self) -> None:
        generated = build_source_lock.build_lock(ROOT)
        committed = json.loads(
            (ROOT / build_source_lock.LOCK_RELATIVE_PATH).read_text(encoding="utf-8")
        )

        self.assertEqual(generated, committed)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить тест, убедиться, что падает**

Run: `python3 -m unittest tests.test_build_source_lock -v`
Expected: FAIL с `ModuleNotFoundError: No module named 'build_source_lock'`

- [ ] **Step 3: Написать генератор**

```python
#!/usr/bin/env python3
"""Собрать lock-файл якорей на текст книги.

Валидатор не обновляет lock самостоятельно: расхождение — ошибка. Обновление
выполняется только этим скриптом и попадает в diff отдельным изменением.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from source_anchors import (
    HEADING,
    LOCAL_SOURCE_ANCHOR,
    LOCK_RELATIVE_PATH,
    SKILL_DIRECTORY,
    anchor_key,
    iter_skill_documents,
)

UPSTREAM_COMMIT = "97de455e9aa44cf9f93441ce0c771c9aa9643d92"
TRANSLATION_COMMIT = "ed2ae516d45dfe26e934cb390b80f105ca780b1f"
LINE_TEXT_LIMIT = 200


def build_lock(root: Path) -> dict:
    anchors: dict[str, dict[str, str]] = {}
    line_cache: dict[Path, list[str]] = {}
    for document in iter_skill_documents(root):
        text = document.read_text(encoding="utf-8")
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
            if not source_path.is_file():
                continue
            if source_path not in line_cache:
                line_cache[source_path] = source_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            lines = line_cache[source_path]
            start = int(match.group("start"))
            if start < 1 or start > len(lines):
                continue
            line = lines[start - 1]
            anchors[anchor_key(match.group("path"), start)] = {
                "line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "line_text": line[:LINE_TEXT_LIMIT],
                "kind": "heading" if HEADING.match(line) else "inline",
            }
    return {
        "schema_version": 1,
        "book": {
            "upstream_commit": UPSTREAM_COMMIT,
            "translation_commit": TRANSLATION_COMMIT,
        },
        "anchors": dict(sorted(anchors.items())),
        "allowed_inline": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the source anchor lock file")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    arguments = parser.parse_args()

    root = arguments.root.resolve()
    lock = build_lock(root)
    lock_path = root / LOCK_RELATIVE_PATH
    lock_path.write_text(
        json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(lock['anchors'])} anchors to {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Сгенерировать lock и проверить объём**

Run: `python3 scripts/build_source_lock.py && python3 -c "import json,pathlib;d=json.loads(pathlib.Path('plugins/developing-ai-agents/skills/developing-ai-agents/references/source-map.lock.json').read_text());print(len(d['anchors']),'anchors');print(sum(1 for v in d['anchors'].values() if v['kind']!='heading'),'non-heading')"`
Expected: не менее 200 уникальных якорей, `0 non-heading`

- [ ] **Step 5: Запустить тесты**

Run: `python3 -m unittest tests.test_build_source_lock -v`
Expected: PASS, 3 теста

- [ ] **Step 6: Commit**

```bash
git add scripts/build_source_lock.py tests/test_build_source_lock.py plugins/developing-ai-agents/skills/developing-ai-agents/references/source-map.lock.json
git commit -m "$(cat <<'EOF'
feat: generate source anchor lock file

Lock фиксирует sha256 строки книги для каждого якоря скилла. Валидатор
сравнивает с ним, поэтому сдвиг текста книги перестаёт быть незаметным.

Обновление lock выполняется только явным запуском скрипта: автоматическое
"залечивание" дрейфа внутри валидатора скрыло бы расхождение от ревьюера.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Проверка L1 — anchor lock в валидаторе

**Files:**
- Modify: `scripts/validate.py` (импорт `source_anchors`, новая функция, вызов в `validate_repository`)
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `source_anchors.anchor_key`, `build_source_lock` не используется валидатором
- Produces: `validate_source_lock(root: Path, errors: list[str]) -> None`

- [ ] **Step 1: Написать падающий тест**

```python
    def test_rejects_anchor_missing_from_lock(self) -> None:
        with repository_copy() as copied_root:
            lock_path = (
                copied_root
                / SKILL_DIRECTORY
                / "references"
                / "source-map.lock.json"
            )
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["anchors"].pop("chapter1.md:13")
            lock_path.write_text(
                json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("anchor missing from lock", result.stdout)
        self.assertIn("chapter1.md:13", result.stdout)

    def test_rejects_anchor_drift(self) -> None:
        with repository_copy() as copied_root:
            lock_path = (
                copied_root
                / SKILL_DIRECTORY
                / "references"
                / "source-map.lock.json"
            )
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["anchors"]["chapter1.md:13"]["line_sha256"] = "0" * 64
            lock_path.write_text(
                json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("anchor drift", result.stdout)
```

- [ ] **Step 2: Запустить тесты, убедиться, что падают**

Run: `python3 -m unittest tests.test_validate.ValidateRepositoryTests.test_rejects_anchor_drift -v`
Expected: FAIL — валидатор возвращает 0, сообщения `anchor drift` нет

- [ ] **Step 3: Реализовать проверку**

В начало `scripts/validate.py` добавить импорт:

```python
import hashlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from source_anchors import (  # noqa: E402
    HEADING,
    LOCAL_SOURCE_ANCHOR,
    LOCK_RELATIVE_PATH,
    anchor_key,
    iter_skill_documents,
    normalize,
    section_text,
)
```

Одновременно **удалить** локальное определение `LOCAL_SOURCE_ANCHOR` из
`scripts/validate.py` (строки 77–80): регексп теперь живёт в одном месте, иначе
два скрипта разойдутся при первой же правке. Существующая проверка диапазонов в
`validate_repository` продолжает использовать импортированный регексп без
изменений.

Добавить функцию перед `validate_repository`:

```python
def load_lock(root: Path, errors: list[str]) -> dict:
    lock_path = root / LOCK_RELATIVE_PATH
    if not lock_path.is_file():
        errors.append(f"missing required file: {LOCK_RELATIVE_PATH.as_posix()}")
        return {}
    try:
        return json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON in {LOCK_RELATIVE_PATH.as_posix()}: {error}")
        return {}


def validate_source_lock(root: Path, lock: dict, errors: list[str]) -> None:
    anchors = lock.get("anchors")
    if not isinstance(anchors, dict):
        errors.append("invalid lock: anchors must be an object")
        return
    line_cache: dict[Path, list[str]] = {}
    for document in iter_skill_documents(root):
        relative_path = document.relative_to(root)
        text = document.read_text(encoding="utf-8")
        for match in LOCAL_SOURCE_ANCHOR.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
            if not source_path.is_file():
                continue
            start = int(match.group("start"))
            key = anchor_key(match.group("path"), start)
            entry = anchors.get(key)
            if entry is None:
                errors.append(
                    f"anchor missing from lock: {key} (referenced in {relative_path})"
                )
                continue
            if source_path not in line_cache:
                line_cache[source_path] = source_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            lines = line_cache[source_path]
            if start > len(lines):
                continue
            digest = hashlib.sha256(lines[start - 1].encode("utf-8")).hexdigest()
            if digest != entry.get("line_sha256"):
                errors.append(
                    f"anchor drift: {key} no longer matches the locked line; "
                    "re-run scripts/build_source_lock.py and review the diff"
                )
```

В `validate_repository` после `validate_plugin_versions(root, errors)` добавить:

```python
    lock = load_lock(root, errors)
    validate_source_lock(root, lock, errors)
```

- [ ] **Step 4: Запустить тесты**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS, включая два новых теста

- [ ] **Step 5: Прогнать валидатор на репозитории**

Run: `python3 scripts/validate.py`
Expected: `Validation passed`

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "$(cat <<'EOF'
feat: verify source anchors against the lock file

Раньше валидатор проверял только, что номер строки не вышел за конец файла:
битую ссылку он ловил, ложную — нет. Теперь sha256 строки книги сверяется
с зафиксированным в lock.

Расхождение сообщает, что нужно перегенерировать lock и просмотреть diff,
а не молча подстраивается под новый текст.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Проверка L2 — якорь указывает на заголовок

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `source_anchors.HEADING`, lock из Task 3
- Produces: расширение `validate_source_lock` — проверка `kind` и `allowed_inline`

- [ ] **Step 1: Написать падающий тест**

```python
    def test_rejects_inline_anchor_without_allowlist(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / SKILL_DIRECTORY / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\n\nПроверка: `references/source-book/chapter1.md:14`.\n",
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(copied_root / "scripts" / "build_source_lock.py")],
                cwd=copied_root,
                check=True,
                capture_output=True,
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("anchor is not a heading", result.stdout)
        self.assertIn("chapter1.md:14", result.stdout)
```

Строка 14 в `chapter1.md` — тело абзаца, а не заголовок; тест опирается на это.

- [ ] **Step 2: Запустить тест, убедиться, что падает**

Run: `python3 -m unittest tests.test_validate.ValidateRepositoryTests.test_rejects_inline_anchor_without_allowlist -v`
Expected: FAIL — сообщения `anchor is not a heading` нет

- [ ] **Step 3: Реализовать проверку**

В `validate_source_lock`, внутри цикла, после проверки дрейфа добавить:

```python
            allowed_inline = lock.get("allowed_inline")
            allowed_keys = (
                {item.get("anchor") for item in allowed_inline}
                if isinstance(allowed_inline, list)
                else set()
            )
            if entry.get("kind") != "heading" and key not in allowed_keys:
                errors.append(
                    f"anchor is not a heading: {key} (referenced in {relative_path}); "
                    "point at a section heading or add it to allowed_inline "
                    "with a reason"
                )
```

Вынести вычисление `allowed_keys` из цикла в начало функции, чтобы не пересчитывать на каждый якорь.

- [ ] **Step 4: Проверить диапазонные якоря**

Добавить в `validate_source_lock` проверку конечной строки диапазона:

```python
            end = int(match.group("end") or start)
            if end < start or end > len(lines):
                errors.append(
                    f"anchor range invalid: {match.group(0)} in {relative_path}"
                )
```

- [ ] **Step 5: Запустить тесты**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "$(cat <<'EOF'
require source anchors to point at headings

Ссылка в середину абзаца хрупка: любая правка книги сдвигает её незаметно,
и проверить такую ссылку глазами дороже. Все 409 существующих якорей уже
указывают на заголовки, поэтому правило закрепляет практику, а не ломает её.

Осознанные исключения перечисляются в allowed_inline с указанием причины.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Проверка L3 — дословная цитата в секции якоря

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `source_anchors.section_text`, `normalize`
- Produces: `CHAPTER_QUOTE: re.Pattern`, `validate_chapter_quotes(root: Path, errors: list[str]) -> None`

- [ ] **Step 1: Написать падающий тест**

```python
    def test_rejects_quote_absent_from_anchor_section(self) -> None:
        with repository_copy() as copied_root:
            chapter_path = (
                copied_root
                / SKILL_DIRECTORY
                / "references"
                / "chapters"
                / "ch01-agent-foundations.md"
            )
            chapter_path.write_text(
                chapter_path.read_text(encoding="utf-8")
                + "\n> «этой фразы нет ни в одной секции книги» — "
                "`references/source-book/chapter1.md:13`\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("quote not found in anchor section", result.stdout)

    def test_accepts_quote_present_in_anchor_section(self) -> None:
        with repository_copy() as copied_root:
            chapter_path = (
                copied_root
                / SKILL_DIRECTORY
                / "references"
                / "chapters"
                / "ch01-agent-foundations.md"
            )
            book_lines = (
                (
                    copied_root
                    / SKILL_DIRECTORY
                    / "references"
                    / "source-book"
                    / "chapter1.md"
                )
                .read_text(encoding="utf-8")
                .splitlines()
            )
            quote = book_lines[12].lstrip("# ").strip()[:60]
            chapter_path.write_text(
                chapter_path.read_text(encoding="utf-8")
                + f"\n> «{quote}» — `references/source-book/chapter1.md:13`\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
```

- [ ] **Step 2: Запустить тесты, убедиться, что первый падает**

Run: `python3 -m unittest tests.test_validate.ValidateRepositoryTests.test_rejects_quote_absent_from_anchor_section -v`
Expected: FAIL — валидатор возвращает 0

- [ ] **Step 3: Реализовать проверку**

Добавить константу рядом с другими регекспами в `scripts/validate.py`:

```python
CHAPTER_QUOTE = re.compile(
    r"^>\s*«(?P<quote>[^»]{3,200})»\s*[—-]\s*`"
    r"(?P<path>references/source-book/[A-Za-z0-9._/-]+\.md):(?P<start>\d+)`",
    re.MULTILINE,
)
CHAPTERS_DIRECTORY = SKILL_DIRECTORY / "references" / "chapters"
```

Добавить функцию:

```python
def validate_chapter_quotes(root: Path, errors: list[str]) -> None:
    chapters_root = root / CHAPTERS_DIRECTORY
    if not chapters_root.is_dir():
        return
    line_cache: dict[Path, list[str]] = {}
    for chapter_path in sorted(chapters_root.glob("*.md")):
        relative_path = chapter_path.relative_to(root)
        text = chapter_path.read_text(encoding="utf-8")
        for match in CHAPTER_QUOTE.finditer(text):
            source_path = root / SKILL_DIRECTORY / match.group("path")
            if not source_path.is_file():
                errors.append(f"source anchor file missing: {match.group('path')}")
                continue
            if source_path not in line_cache:
                line_cache[source_path] = source_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            start = int(match.group("start"))
            haystack = section_text(line_cache[source_path], start)
            needle = normalize(match.group("quote"))
            if needle not in haystack:
                errors.append(
                    "quote not found in anchor section: "
                    f"{relative_path} -> {match.group('path')}:{start}"
                )
```

Вызвать в `validate_repository` после `validate_source_lock(root, lock, errors)`:

```python
    validate_chapter_quotes(root, errors)
```

Проверка «в конспекте есть хотя бы одна цитата» здесь **не** добавляется: до фазы 1 ни один из 12 конспектов цитат не содержит, и валидатор оставил бы фазу 0 красной. Она включается в Task 18, когда все конспекты переписаны.

- [ ] **Step 4: Запустить тесты**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS, оба новых теста

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "$(cat <<'EOF'
feat: verify chapter quotes against the anchored section

Конспект главы пересказывает книгу, поэтому каждое утверждение о её
содержании несёт дословный фрагмент. Валидатор ищет фрагмент внутри секции
якоря — от заголовка до следующего заголовка того же или более высокого
уровня.

Окно ограничено секцией, а не числом строк: медианная секция chapter2.md —
16 строк, тогда как окно ±40 строк захватывает соседние разделы и
пропускает цитату, взятую не из того места.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Лимит SKILL.md и покрытие роутера

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: ничего нового
- Produces: `SKILL_LINE_LIMIT: int`, `REFERENCE_PATH: re.Pattern`, `validate_skill_routing(root: Path, errors: list[str]) -> None`

- [ ] **Step 1: Написать падающий тест**

```python
    def test_rejects_reference_file_missing_from_skill(self) -> None:
        with repository_copy() as copied_root:
            orphan_path = (
                copied_root / SKILL_DIRECTORY / "references" / "orphan-note.md"
            )
            orphan_path.write_text("# Осиротевший файл\n", encoding="utf-8")

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("reference file not listed in SKILL.md", result.stdout)
        self.assertIn("orphan-note.md", result.stdout)

    def test_rejects_skill_listing_missing_reference(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / SKILL_DIRECTORY / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\n- `references/playbooks/nonexistent.md`\n",
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("SKILL.md lists missing reference file", result.stdout)

    def test_rejects_oversized_skill_document(self) -> None:
        with repository_copy() as copied_root:
            skill_path = copied_root / SKILL_DIRECTORY / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8") + "\nстрока\n" * 400,
                encoding="utf-8",
            )

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("SKILL.md exceeds", result.stdout)
```

- [ ] **Step 2: Запустить тесты, убедиться, что падают**

Run: `python3 -m unittest tests.test_validate.ValidateRepositoryTests.test_rejects_oversized_skill_document -v`
Expected: FAIL

- [ ] **Step 3: Реализовать проверку**

Добавить константы:

```python
SKILL_LINE_LIMIT = 300
REFERENCE_PATH = re.compile(r"references/[A-Za-z0-9._/-]+\.md")
```

Добавить функцию:

```python
def validate_skill_routing(root: Path, errors: list[str]) -> None:
    skill_path = root / SKILL_DIRECTORY / "SKILL.md"
    if not skill_path.is_file():
        return
    text = skill_path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if line_count > SKILL_LINE_LIMIT:
        errors.append(
            f"SKILL.md exceeds {SKILL_LINE_LIMIT} lines: {line_count}; "
            "move detail into references/"
        )

    listed = {
        match.group(0)
        for match in REFERENCE_PATH.finditer(text)
        if "source-book/" not in match.group(0)
    }
    references_root = root / SKILL_DIRECTORY / "references"
    present = {
        path.relative_to(root / SKILL_DIRECTORY).as_posix()
        for path in references_root.rglob("*.md")
        if "source-book" not in path.parts
    }
    for missing in sorted(present - listed):
        errors.append(f"reference file not listed in SKILL.md: {missing}")
    for dangling in sorted(listed - present):
        errors.append(f"SKILL.md lists missing reference file: {dangling}")
```

Вызвать в `validate_repository` после `validate_chapter_quotes(root, errors)`.

- [ ] **Step 4: Привести SKILL.md в соответствие**

Текущий `SKILL.md` ссылается на `references/chapters/index.md`. Удалить файл `index.md` и заменить ссылку на строку с перечислением 12 конспектов:

```markdown
- Подробные главы: `references/chapters/ch00-introduction.md`, `references/chapters/ch01-agent-foundations.md`, `references/chapters/ch02-context-engineering.md`, `references/chapters/ch03-memory-and-knowledge.md`, `references/chapters/ch04-tools.md`, `references/chapters/ch05-coding-agents.md`, `references/chapters/ch06-evaluation.md`, `references/chapters/ch07-post-training.md`, `references/chapters/ch08-self-evolution.md`, `references/chapters/ch09-realtime-multimodal.md`, `references/chapters/ch10-multi-agent.md`, `references/chapters/ch11-afterword.md`
```

- [ ] **Step 5: Запустить всё**

Run: `python3 scripts/build_source_lock.py && python3 scripts/validate.py && python3 -m unittest discover -s tests -v`
Expected: `Validation passed`, все тесты зелёные

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py plugins/developing-ai-agents/skills/developing-ai-agents/SKILL.md
git rm plugins/developing-ai-agents/skills/developing-ai-agents/references/chapters/index.md
git commit -m "$(cat <<'EOF'
feat: enforce skill routing coverage and size budget

Роутер полезен, только если он полон: файл, не упомянутый в SKILL.md,
агент не найдёт, а ссылка на несуществующий файл тратит его ход. Проверка
работает в обе стороны.

index.md удалён: промежуточный хаб заставляет агента читать целевой файл
частично, поэтому все конспекты линкуются из SKILL.md напрямую.

Лимит в 300 строк удерживает постоянный контекстный налог: SKILL.md
загружается при каждом срабатывании скилла.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Фаза 1. Конспекты глав

Задачи 7–18 одинаковы по форме и отличаются главой и списком тем. Цикл каждой:

1. добавить строку конспекта в роутер `SKILL.md` (если её ещё нет после Task 6) и убедиться, что валидатор падает с `SKILL.md lists missing reference file` — RED;
2. написать конспект по скелету из шапки плана, покрыв все темы главы;
3. `python3 scripts/build_source_lock.py` — внести новые якоря в lock;
4. `python3 scripts/validate.py` — GREEN;
5. проверить покрытие: каждая тема главы из `references/source-map.md` раскрыта;
6. commit.

Файлы конспектов уже существуют (45–94 строки) и **переписываются целиком**: текущее содержание — тезисы без цитат, оно не удовлетворяет ни скелету, ни гейту L3.

### Task 7: Конспект введения (ch00)

**Files:**
- Modify: `.../references/chapters/ch00-introduction.md`

**Темы для покрытия** (из `source-map.md`): назначение и структура книги — `introduction.md:3`, `introduction.md:39`, `introduction.md:58`.

- [ ] **Step 1: Убедиться, что валидатор проходит до правки** — `python3 scripts/validate.py`
- [ ] **Step 2: Переписать файл по скелету, покрыв три темы, с цитатой в «Что решает глава» и в каждом механизме**
- [ ] **Step 3: `python3 scripts/build_source_lock.py`**
- [ ] **Step 4: `python3 scripts/validate.py`** — Expected: `Validation passed`
- [ ] **Step 5: Commit** — `docs: rewrite ch00 summary with verified quotes`

### Task 8: Конспект главы 1 — основы агентов (ch01)

**Files:**
- Modify: `.../references/chapters/ch01-agent-foundations.md`

**Темы:** формула LLM + контекст + инструменты (`chapter1.md:13`); цикл ReAct (`:146`); Harness-инженерия и пять функций (`:230`, `:272`, `:280`); простота, прозрачность, ACI, граница workflow/agent (`:295`, `:324`); guardrails и безопасность (`:387`).

- [ ] **Step 1: Переписать файл по скелету, раскрыв пять тем как механизмы**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`** — Expected: `Validation passed`
- [ ] **Step 4: Проверить, что таблица пяти функций Harness согласована с `SKILL.md`** (Context, Tools, Constraints, Verification, Correction — те же названия)
- [ ] **Step 5: Commit** — `docs: rewrite ch01 summary with verified quotes`

### Task 9: Конспект главы 2 — инженерия контекста (ch02)

**Files:**
- Modify: `.../references/chapters/ch02-context-engineering.md`

**Темы:** структура API-контекста (`chapter2.md:34`, `:355`); KV-cache как ограничение архитектуры (`:401`, `:524`); prompt и tool definitions (`:560`, `:635`); prompt injection (`:655`); dynamic prompts и Skills (`:689`, `:700`, `:722`); Agent Status Bar (`:763`, `:842`, `:856`); сжатие и изоляция контекста (`:936`, `:1017`, `:1054`).

- [ ] **Step 1: Переписать файл по скелету, раскрыв семь тем**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`** — Expected: `Validation passed`
- [ ] **Step 4: Commit** — `docs: rewrite ch02 summary with verified quotes`

### Task 10: Конспект главы 3 — память и знания (ch03)

**Files:**
- Modify: `.../references/chapters/ch03-memory-and-knowledge.md`

**Темы:** трёхуровневая оценка памяти (`chapter3.md:49`); иерархия и четыре формата памяти (`:78`, `:94`); privacy памяти (`:261`); RAG, hybrid search, Agentic RAG (`:273`, `:425`, `:574`); contextual retrieval (`:630`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch03 summary with verified quotes`

### Task 11: Конспект главы 4 — инструменты (ch04)

**Files:**
- Modify: `.../references/chapters/ch04-tools.md`

**Темы:** классы и проектирование tools (`chapter4.md:14`, `:41`); MCP и выбор инструментов (`:110`); perception, execution, collaboration tools (`:147`, `:179`, `:284`); async/event-driven agent (`:347`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch04 summary with verified quotes`

### Task 12: Конспект главы 5 — coding agents (ch05)

**Files:**
- Modify: `.../references/chapters/ch05-coding-agents.md`

**Темы:** Coding Agent, Sessionless-архитектура, безопасность (`chapter5.md:15`, `:82`, `:92`); Harness и recovery (`:188`, `:233`); code as meta-capability (`:354`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch05 summary with verified quotes`

### Task 13: Конспект главы 6 — оценка (ch06)

**Files:**
- Modify: `.../references/chapters/ch06-evaluation.md`

**Темы:** evaluation environment и dataset (`chapter6.md:71`, `:157`); метрики и LLM-as-a-Judge (`:239`, `:284`); model/system selection и cost (`:421`, `:444`); statistics и observability (`:520`, `:534`); improvement loop, ablation, simulation (`:563`, `:635`, `:679`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch06 summary with verified quotes`

### Task 14: Конспект главы 7 — post-training (ch07)

**Files:**
- Modify: `.../references/chapters/ch07-post-training.md`

**Темы:** pretraining/SFT/RL (`chapter7.md:27`, `:72`, `:305`); данные и среда важнее алгоритма (`:447`); multi-turn reward и RLVP (`:481`, `:581`); tool-call RL и On-Policy Distillation (`:635`, `:694`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch07 summary with verified quotes`

### Task 15: Конспект главы 8 — самоэволюция (ch08)

**Files:**
- Modify: `.../references/chapters/ch08-self-evolution.md`

**Темы:** три парадигмы обучения (`chapter8.md:23`); experience, failures, Skills (`:53`, `:105`, `:113`); prompt optimization и cross-session continuation (`:145`, `:181`); tool discovery/creation (`:187`, `:236`, `:273`); continuous accumulation и safety (`:319`, `:329`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch08 summary with verified quotes`

### Task 16: Конспект главы 9 — realtime и мультимодальность (ch09)

**Files:**
- Modify: `.../references/chapters/ch09-realtime-multimodal.md`

**Темы:** Cascading, Omni, Full-Duplex (`chapter9.md:28`, `:42`, `:149`, `:174`); fast/slow thinking (`:192`, `:276`); Computer Use и realtime (`:308`, `:418`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch09 summary with verified quotes`

### Task 17: Конспект главы 10 — multi-agent (ch10)

**Files:**
- Modify: `.../references/chapters/ch10-multi-agent.md`

**Темы:** оси context/topology (`chapter10.md:11`, `:15`, `:53`); когда multi-agent выигрывает (`:65`); shared/no-shared context (`:94`, `:196`); data/control planes и топологии (`:206`, `:237`, `:251`, `:287`, `:431`); file conflicts и каскадные ошибки (`:481`, `:493`, `:511`).

- [ ] **Step 1: Переписать файл по скелету**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: rewrite ch10 summary with verified quotes`

### Task 18: Конспект послесловия (ch11)

**Files:**
- Modify: `.../references/chapters/ch11-afterword.md`

**Темы:** возврат к основной формуле (`afterword.md:3`).

- [ ] **Step 1: Переписать файл по скелету; для короткого послесловия разделы «Таблицы решений» и «Failure modes» опускаются**
- [ ] **Step 2: `python3 scripts/build_source_lock.py`**
- [ ] **Step 3: `python3 scripts/validate.py`**
- [ ] **Step 4: Включить проверку «конспект без цитат»**

Все 12 конспектов теперь содержат цитаты, поэтому проверку можно активировать.
В `validate_chapter_quotes`, внутри цикла по `chapter_path`, добавить:

```python
        if not CHAPTER_QUOTE.search(text):
            errors.append(f"chapter summary without verified quotes: {relative_path}")
```

Проверка ловит конспект, пересказывающий книгу без единой сверяемой ссылки. Она
не заменяет требование цитаты в каждом механизме — оно остаётся правилом для
автора, потому что «механизм» машинно не распознаётся.

- [ ] **Step 5: Добавить тест на новую проверку** в `tests/test_validate.py`

```python
    def test_rejects_chapter_summary_without_quotes(self) -> None:
        with repository_copy() as copied_root:
            chapter_path = (
                copied_root
                / SKILL_DIRECTORY
                / "references"
                / "chapters"
                / "ch11-afterword.md"
            )
            chapter_path.write_text("# Послесловие\n\nБез цитат.\n", encoding="utf-8")

            result = run_validator(copied_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("chapter summary without verified quotes", result.stdout)
```

- [ ] **Step 6: `python3 scripts/validate.py && python3 -m unittest discover -s tests -v`**
- [ ] **Step 7: Commit** — `docs: rewrite ch11 summary and require quotes in every chapter file`

---

## Фаза 2. Паттерны и антипаттерны

### Task 19: Расширить patterns.md до 16 паттернов

**Files:**
- Modify: `.../references/patterns.md`

**Interfaces:**
- Consumes: конспекты глав из Задач 7–18
- Produces: паттерны 13–16, на которые ссылаются playbooks Задач 21–27

- [ ] **Step 1: Добавить оглавление в начало файла** (16 пунктов, файл длиннее 100 строк)
- [ ] **Step 2: Добавить в каждый существующий паттерн 1–12 раздел «Сигналы, что паттерн нужен» и «Стоимость применения»**
- [ ] **Step 3: Написать паттерн 13 «Grounded Retrieval Layer»** — hybrid search, contextual retrieval, Agentic RAG; provenance фрагмента, проверка релевантности, деградация при пустой выдаче. Источники: `references/source-book/chapter3.md:273`, `:425`, `:574`, `:630`
- [ ] **Step 4: Написать паттерн 14 «Sessionless Resumable Worker»** — восстановление из durable state после рестарта, идемпотентность повторного шага. Источники: `references/source-book/chapter5.md:82`, `:233`, `references/source-book/chapter8.md:181`
- [ ] **Step 5: Написать паттерн 15 «Post-Training Decision Gate»** — когда fine-tuning оправдан, а когда это подмена отсутствующего eval-loop. Источники: `references/source-book/chapter7.md:27`, `:447`, `references/source-book/chapter8.md:23`
- [ ] **Step 6: Написать паттерн 16 «Untrusted Content Firewall»** — изоляция недоверенного retrieved/tool-контента от инструкций и permissions. Источники: `references/source-book/chapter2.md:655`, `references/source-book/chapter4.md:179`
- [ ] **Step 7: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`** — Expected: `Validation passed`
- [ ] **Step 8: Commit** — `docs: extend patterns to sixteen with retrieval, resume, post-training and injection defence`

### Task 20: Каталог антипаттернов

**Files:**
- Create: `.../references/antipatterns.md`
- Modify: `.../SKILL.md` (добавить в список файлов)

- [ ] **Step 1: Добавить `references/antipatterns.md` в список файлов SKILL.md**
- [ ] **Step 2: `python3 scripts/validate.py`** — Expected: FAIL с `SKILL.md lists missing reference file: references/antipatterns.md`
- [ ] **Step 3: Написать каталог.** Формат записи: `## Симптом` → «Как выглядит» → «Почему возникает» → «Чем заменить» → «Ссылка на паттерн/главу».

Обязательные двенадцать записей: система промптов растёт без удаления; полный tool output inline; свободное summary без schema; перегенерация префикса на каждом ходу; передача ребёнку всей истории родителя; retrieved content как инструкция; единичная неудача как правило; самооценка агента вместо внешней проверки; multi-agent ради дебатов; отсутствие terminal state; необратимое действие без approval; тюнинг на holdout.

Дополнить записями из разделов «Антипаттерны» конспектов Задач 7–18 — итоговый объём определяется тем, что реально нашлось в главах, а не заданным числом
- [ ] **Step 4: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`** — Expected: `Validation passed`
- [ ] **Step 5: Commit** — `docs: add antipattern catalogue indexed by symptom`

---

## Фаза 3. Playbooks

Каждая задача: добавить строку в роутер `SKILL.md` → валидатор падает (RED) → написать playbook по скелету → валидатор проходит (GREEN) → commit.

### Task 21: Playbook проектирования агента

**Files:**
- Create: `.../references/playbooks/design-agent.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера** — `спроектировать агента с нуля | references/playbooks/design-agent.md | references/patterns.md, references/templates/agent-design.md`
- [ ] **Step 2: `python3 scripts/validate.py`** — Expected: FAIL, `SKILL.md lists missing reference file`
- [ ] **Step 3: Написать playbook.** Шаги: собрать требования и ограничения → определить, нужен ли агент вообще (лестница: один вызов → workflow → агент → multi-agent) → зафиксировать контракт задачи и acceptance criteria → спроектировать context lifecycle → определить инструменты и права → задать terminal states и бюджеты → определить проверки и eval-план. Гейт после каждого шага
- [ ] **Step 4: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 5: Commit** — `docs: add design-agent playbook`

### Task 22: Playbook разбора trace

**Files:**
- Create: `.../references/playbooks/diagnose-trace.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: собрать trace, конфиг, версии → построить таблицу шагов (действие, наблюдение, изменение состояния) → локализовать дефект по четырём областям (LLM / контекст / инструменты / Harness) → отделить evidence от inference и unknown → сформулировать одну проверяемую гипотезу → предложить измерение, которое её опровергнет. Гейт: не предлагать исправление, пока гипотеза не проверена
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add diagnose-trace playbook`

### Task 23: Playbook review Harness

**Files:**
- Create: `.../references/playbooks/harness-review.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: пройти пять функций Harness по очереди (Context, Tools, Constraints, Verification, Correction) → для каждой найти в коде механизм и его отсутствие → проверить terminal states и бюджеты → проверить, что каждое действие оставляет наблюдение → выписать находки как «симптом → риск → минимальное исправление». Гейт: не переходить к рекомендациям, пока не найдено подтверждение в коде
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add harness-review playbook`

### Task 24: Playbook построения evals

**Files:**
- Create: `.../references/playbooks/build-evals.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: зафиксировать версии (модель, prompt, tools, данные, среда) → собрать задачи из реального распределения → отделить holdout и adversarial → выбрать внешне проверяемый outcome → задать метрики (успех, нарушения, ошибки инструментов, latency/tokens/cost, recovery) → задать число повторов и release gate → определить canary и rollback. Гейт: не оптимизировать, пока baseline не зафиксирован
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add build-evals playbook`

### Task 25: Playbook проектирования памяти

**Files:**
- Create: `.../references/playbooks/memory-design.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: сопоставить три механизма (post-training, in-context, externalized) → выбрать носитель по типу знания → задать typed schema, provenance и retention → спроектировать цепочку `episode → extraction → candidate → review → promotion` → задать защиту от отравления и запрос на удаление → задать rollback производных артефактов. Гейт: не превращать единичную неудачу в правило
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add memory-design playbook`

### Task 26: Playbook realtime-бюджета

**Files:**
- Create: `.../references/playbooks/realtime-latency.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: сравнить три парадигмы (Cascading, Omni, Full-Duplex) → задать latency budget и разложить по стадиям → разделить fast interaction loop и slow reasoning → задать `turn_id`, версию состояния, deadline и cancellation → определить поведение устаревшего результата → задать сценарии проверки (barge-in, частичный ASR, потеря сети). Гейт: провизорный бюджет объявляется гипотезой, а не отраслевым фактом
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add realtime-latency playbook`

### Task 27: Playbook выбора multi-agent

**Files:**
- Create: `.../references/playbooks/multi-agent-choice.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить строку роутера, убедиться в падении валидатора**
- [ ] **Step 2: Написать playbook.** Шаги: проверить, даёт ли роль новое внешнее свидетельство → сравнить с single-agent при равном token/tool/time budget → выбрать оси (shared/isolated context, peer/manager/decentralized) → разделить data plane и control plane → задать ownership файлов и политику конфликтов → спроектировать независимого verifier → измерить каскадные ошибки (`false_accept`, `cascade_depth`). Гейт: не добавлять роль без наблюдаемого выигрыша при равном бюджете
- [ ] **Step 3: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 4: Commit** — `docs: add multi-agent-choice playbook`

---

## Фаза 4. Шаблоны

### Task 28: Шаблоны проектирования

**Files:**
- Create: `.../references/templates/agent-design.md`, `.../references/templates/harness-spec.md`, `.../references/templates/tool-contract.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить три пути в список файлов SKILL.md, убедиться в падении валидатора**
- [ ] **Step 2: Написать `agent-design.md`** — обязательные поля: задача и acceptance criteria, выбранный уровень архитектуры и что отвергнуто, контекстный контракт, инструменты, terminal states и бюджеты, проверки, риски и rollback. Один заполненный пример
- [ ] **Step 3: Написать `harness-spec.md`** — по пяти функциям: механизм, где реализован, чем проверяется, что происходит при отказе. Один заполненный пример
- [ ] **Step 4: Написать `tool-contract.md`** — обязательные поля: capability, schema входа/выхода, preconditions, side effects, timeout, retry, idempotency key, коды ошибок с `retryable` и `remediation`, permissions, sandbox, требуется ли approval. Один заполненный пример
- [ ] **Step 5: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 6: Commit** — `docs: add agent design, harness and tool contract templates`

### Task 29: Шаблоны проверки и эксплуатации

**Files:**
- Create: `.../references/templates/eval-plan.md`, `.../references/templates/memory-policy.md`, `.../references/templates/trace-diagnosis.md`
- Modify: `.../SKILL.md`

- [ ] **Step 1: Добавить три пути в список файлов SKILL.md, убедиться в падении валидатора**
- [ ] **Step 2: Написать `eval-plan.md`** — обязательные поля: зафиксированные версии, состав наборов (dev/holdout/adversarial), oracle или rubric, метрики, число повторов и интервалы, release gate, canary, rollback. Один заполненный пример
- [ ] **Step 3: Написать `memory-policy.md`** — обязательные поля: типы записей и их schema, provenance, retention и удаление, scope и видимость, процесс promotion, защита от отравления, rollback производных. Один заполненный пример
- [ ] **Step 4: Написать `trace-diagnosis.md`** — обязательные поля: наблюдаемый симптом, таблица шагов, локализация по четырём областям, evidence / inference / unknown, гипотеза, опровергающее измерение, минимальное исправление. Один заполненный пример
- [ ] **Step 5: `python3 scripts/build_source_lock.py && python3 scripts/validate.py`**
- [ ] **Step 6: Commit** — `docs: add eval plan, memory policy and trace diagnosis templates`

---

## Фаза 5. Сборка SKILL.md и справочников

### Task 30: Финальная сборка SKILL.md, cheatsheet, glossary, source-map

**Files:**
- Modify: `.../SKILL.md`, `.../references/cheatsheet.md`, `.../references/glossary.md`, `.../references/source-map.md`

- [ ] **Step 1: Собрать роутер в SKILL.md** в виде таблицы «Запрос выглядит как | Начни с | Добери при необходимости» по девяти строкам из §6 спеки
- [ ] **Step 2: Собрать под роутером список всех файлов `references/` с однострочным назначением** (кроме `source-book/`)
- [ ] **Step 3: Сократить ядро SKILL.md**, вынеся детализацию в соответствующие слои: разделы, полностью дублирующие конспект главы или playbook, заменить одной строкой решения и ссылкой
- [ ] **Step 4: Проверить лимит** — `python3 -c "import pathlib;p=pathlib.Path('plugins/developing-ai-agents/skills/developing-ai-agents/SKILL.md');print(len(p.read_text().splitlines()),'lines')"` — Expected: не более 300
- [ ] **Step 5: Обновить `cheatsheet.md`** — добавить колонку «куда идти» со ссылками на playbooks
- [ ] **Step 6: Обновить `glossary.md`** — внести термины, введённые в новых паттернах и playbooks (`Grounded Retrieval Layer`, `cascade_depth`, `false_accept`, `capability token`, `durable state`)
- [ ] **Step 7: Обновить `source-map.md`** — добавить колонку «конспект», связывающую тему с файлом `chapters/chNN`
- [ ] **Step 8: `python3 scripts/build_source_lock.py && python3 scripts/validate.py && python3 -m unittest discover -s tests -v`**
- [ ] **Step 9: Commit** — `docs: assemble task router and synchronise reference index`

---

## Фаза 6. Evals

### Task 31: Расширить набор сценариев до 26

**Files:**
- Modify: `plugins/developing-ai-agents/evals/evals.json`

**Interfaces:**
- Consumes: playbooks Задач 21–27, шаблоны Задач 28–29
- Produces: `evals.json` с 26 записями формата `{id, prompt, expected_output, files}`

- [ ] **Step 1: Прочитать текущий формат** — `python3 -c "import json;d=json.load(open('plugins/developing-ai-agents/evals/evals.json'));print(json.dumps(d['evals'][0],ensure_ascii=False,indent=2))"`
- [ ] **Step 2: Пересмотреть 12 существующих сценариев** — привести `expected_output` в соответствие с новыми playbooks и шаблонами
- [ ] **Step 3: Добавить 14 новых сценариев** так, чтобы каждый playbook был затронут минимум двумя, а каждый шаблон — минимум одним. Промпты — реалистичные запросы с конкретикой (пути файлов, названия сервисов, числа), а не абстракции
Каждой записи добавить поле `covers` — список файлов скилла, которые сценарий проверяет. Промпт пишется от лица пользователя и имён файлов не содержит, поэтому измерить покрытие поиском по тексту промпта невозможно:

```json
{
  "id": 13,
  "prompt": "…",
  "expected_output": "…",
  "files": [],
  "covers": ["references/playbooks/design-agent.md", "references/templates/agent-design.md"]
}
```

- [ ] **Step 4: Проверить покрытие скриптом**

```bash
python3 - <<'PY'
import collections, json, pathlib

evals = json.load(open('plugins/developing-ai-agents/evals/evals.json'))['evals']
skill = pathlib.Path('plugins/developing-ai-agents/skills/developing-ai-agents')
counts = collections.Counter(target for item in evals for target in item.get('covers', []))

print(len(evals), 'сценариев')
problems = []
for group, minimum in (('playbooks', 2), ('templates', 1)):
    for path in sorted((skill / 'references' / group).glob('*.md')):
        key = f'references/{group}/{path.name}'
        got = counts.get(key, 0)
        print(f'{key:52} {got}')
        if got < minimum:
            problems.append(f'{key}: {got} < {minimum}')
for target in counts:
    if not (skill / target).is_file():
        problems.append(f'covers ссылается на несуществующий файл: {target}')
if len(evals) != 26:
    problems.append(f'сценариев {len(evals)}, ожидалось 26')
print('OK' if not problems else 'НЕ ГОТОВО: ' + '; '.join(problems))
PY
```

Expected: `26 сценариев` и `OK`

- [ ] **Step 5: `python3 scripts/validate.py`** — Expected: `Validation passed` (JSON валиден)
- [ ] **Step 6: Commit** — `test: extend eval suite to twenty-six scenarios`

### Task 32: Триггерные evals

**Files:**
- Modify: `plugins/developing-ai-agents/evals/trigger-evals.json`

- [ ] **Step 1: Прочитать текущий формат** — `python3 -c "import json;d=json.load(open('plugins/developing-ai-agents/evals/trigger-evals.json'));print(json.dumps(d,ensure_ascii=False)[:400])"`
- [ ] **Step 2: Написать 10 позитивных запросов** — разные формулировки: формальные и разговорные, с опечатками, без прямого называния «агент»; включить случаи, где скилл конкурирует с другим, но должен выиграть
- [ ] **Step 3: Написать 10 near-miss негативов** — запросы, делящие ключевые слова, но требующие другого: обычный REST-бэкенд с очередью, оптимизация одиночного промпта для суммаризации, починка упавшего CI, классический ETL на Airflow, чат-бот на правилах без внешних действий, выбор векторной БД для поиска по документам без агента, настройка Prometheus-алертов, рефакторинг Python-модуля, генерация текста по шаблону, интеграция платёжного API
- [ ] **Step 4: Проверить баланс**

```bash
python3 - <<'PY'
import json
d = json.load(open('plugins/developing-ai-agents/evals/trigger-evals.json'))
queries = d['queries']
positive = sum(1 for q in queries if q.get('should_trigger'))
print(len(queries), 'запросов;', positive, 'позитивных;', len(queries)-positive, 'негативных')
PY
```

Expected: `20 запросов; 10 позитивных; 10 негативных`

- [ ] **Step 5: `python3 scripts/validate.py`**
- [ ] **Step 6: Commit** — `test: balance trigger evals with ten near-miss negatives`

---

## Фаза 7. Выпуск

### Task 33: Версия 0.5.0, README и финальная проверка

**Files:**
- Modify: `plugins/developing-ai-agents/.claude-plugin/plugin.json`, `plugins/developing-ai-agents/.codex-plugin/plugin.json`, `README.md`

- [ ] **Step 1: Поднять версию до 0.5.0 в обоих манифестах** (значения обязаны совпадать — это проверяет `validate_plugin_versions`)
- [ ] **Step 2: Обновить раздел «Состав» в README** — добавить playbooks, templates, antipatterns, lock-файл
- [ ] **Step 3: Добавить в README раздел «Проверка достоверности»** — описать трёхуровневый гейт и команду `python3 scripts/build_source_lock.py`
- [ ] **Step 4: Прогнать все проверки**

```bash
python3 scripts/build_source_lock.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
ruff format --check scripts tests
ruff check scripts tests
claude plugin validate . --strict
claude plugin validate plugins/developing-ai-agents --strict
```

Expected: все команды завершаются успешно

- [ ] **Step 5: Проверить критерии приёмки спеки**

```bash
python3 - <<'PY'
import json, pathlib, re
skill = pathlib.Path('plugins/developing-ai-agents/skills/developing-ai-agents')
print('SKILL.md строк:', len((skill/'SKILL.md').read_text().splitlines()))
for group in ('chapters','playbooks','templates'):
    files = sorted((skill/'references'/group).glob('*.md'))
    print(f'{group}: {len(files)} файлов')
    for f in files:
        text = f.read_text()
        toc = 'Оглавление' in text
        quotes = len(re.findall(r'^>\s*«', text, re.M))
        print(f'   {f.name:34} {len(text.splitlines()):4} строк  TOC={toc}  цитат={quotes}')
lock = json.loads((skill/'references'/'source-map.lock.json').read_text())
print('якорей в lock:', len(lock['anchors']))
PY
```

Expected: `SKILL.md` ≤300 строк; 12 конспектов с TOC и цитатами; 7 playbooks; 6 шаблонов

- [ ] **Step 6: Commit** — `release: version 0.5.0 with expanded reference library`

---

## Фаза 8. Benchmark (только по явному разрешению пользователя)

### Task 34: Прогон benchmark v3

**Files:**
- Create: `plugins/developing-ai-agents/benchmarks/v3/benchmark.json`, `benchmark.md`, `trigger-metrics.json`
- Modify: `README.md` (таблица результатов)

**Предусловие:** пользователь явно разрешил запуск субагентов. Без разрешения задача не выполняется — фаза 7 является завершением работы.

- [ ] **Step 1: Спросить разрешение и уточнить бюджет** — 26 сценариев × 2 конфигурации = 52 запуска
- [ ] **Step 2: Снять снапшот текущего скилла как baseline** — `cp -r plugins/developing-ai-agents/skills/developing-ai-agents .tmp/skill-snapshot-0.4.0`
- [ ] **Step 3: Прогнать 26 сценариев с новым скиллом и 26 со снапшотом 0.4.0**
- [ ] **Step 4: Свести результаты в `benchmarks/v3/benchmark.json`** в формате существующего `benchmarks/v2/benchmark.json`
- [ ] **Step 5: Прогнать trigger-evals и записать `trigger-metrics.json`**
- [ ] **Step 6: Обновить таблицу результатов в README с указанием, что сравнение идёт против версии 0.4.0, а не против отсутствия скилла**
- [ ] **Step 7: Commit** — `test: record benchmark v3 against the 0.4.0 baseline`
