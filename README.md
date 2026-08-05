# Developing AI Agents

Плагин для Codex и Claude Code с навыком `developing-ai-agents` для разработки
и проверки AI-агентов. Материалы основаны на книге Bojie Li
«深入理解 AI Agent：设计原理与工程实践».

Текст русского перевода хранится внутри плагина. Для работы с ним не требуется
отдельно скачивать репозиторий книги.

## Установка

### Codex

```bash
codex plugin marketplace add ilkruglov/developing-ai-agents-skill
codex plugin add developing-ai-agents@developing-ai-agents-skill
```

Для обновления:

```bash
codex plugin marketplace upgrade developing-ai-agents-skill
codex plugin add developing-ai-agents@developing-ai-agents-skill
```

### Claude Code

```bash
claude plugin marketplace add ilkruglov/developing-ai-agents-skill
claude plugin install developing-ai-agents@developing-ai-agents-skill
```

Для обновления:

```bash
claude plugin marketplace update developing-ai-agents-skill
claude plugin update developing-ai-agents@developing-ai-agents-skill
```

После установки или обновления начните новую сессию Codex или Claude Code.

## Использование

```text
Используй $developing-ai-agents, чтобы спроектировать агента для моей задачи.
```

В Claude Code skill также доступен как команда:

```text
/developing-ai-agents:developing-ai-agents Спроектируй агента для моей задачи.
```

Skill применяется также при review, отладке и оценке существующих агентных
систем.

## Состав

- `plugins/developing-ai-agents/skills/developing-ai-agents/` — Skill и
  материалы книги.
- `plugins/developing-ai-agents/evals/` — набор проверочных задач.
- `plugins/developing-ai-agents/benchmarks/v2/` — сохранённые результаты
  benchmark.
- `scripts/validate.py` — проверка структуры репозитория.

## Проверка

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate plugins/developing-ai-agents --strict
```

## Результаты evals

Набор содержит 12 сценариев, по три запуска с навыком и без него.

| Метрика | С навыком | Без навыка |
|---|---:|---:|
| Выполненные требования | 90,0% (162/180) | 75,0% (135/180) |
| Победы в слепом сравнении | 28/36 | 8/36 |
| Точность определения применимости | 100% | — |

Модель запуска, расход токенов и время не записывались. Задачи внутри одного
контекста запуска не были полностью независимы. Исходные данные находятся в
[`plugins/developing-ai-agents/benchmarks/v2/`](plugins/developing-ai-agents/benchmarks/v2/).

## Автор книги и исходные материалы

- Автор: [Bojie Li](https://github.com/bojieli).
- Оригинал: [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book).
- Русский перевод: [ilkruglov/ai-agent-book](https://github.com/ilkruglov/ai-agent-book),
  «Русский перевод: community edition».

Версии исходных материалов указаны в [`SOURCE.json`](SOURCE.json). Уведомление
об авторстве находится в [`NOTICE`](NOTICE).

## Лицензия

Apache License 2.0. См. [`LICENSE`](LICENSE).
