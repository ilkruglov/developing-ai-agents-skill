# Developing AI Agents

`developing-ai-agents` — плагин для Codex и Claude Code, который помогает
проектировать, реализовывать, отлаживать и оценивать AI-агентов как проверяемые
системы. Он разбирает задачу на LLM, контекст, инструменты и Harness, выбирает
минимальную достаточную архитектуру и сразу определяет, как проверить результат.

Методическая основа skill — книга Bojie Li «AI-агенты изнутри: принципы
проектирования и инженерная практика». Русский текст книги и рабочие материалы
включены в плагин: отдельно скачивать книгу, выбирать главы или собирать skill
вручную не требуется.

## Задачи, которые покрывает skill

- **Выбор архитектуры.** Сравнивает один вызов модели, детерминированный
  workflow, одного автономного агента и multi-agent; рекомендует первый вариант,
  который действительно закрывает задачу.
- **Harness и надёжность.** Проектирует контур Context → Tools → Constraints →
  Verification → Correction с лимитами, terminal states, retry, rollback и
  восстановлением после сбоев.
- **Контекст, состояние и память.** Разделяет стабильные инструкции, динамическую
  траекторию, рабочее состояние, event log, RAG и долговременную memory; задаёт
  правила сжатия, provenance и retention.
- **Инструменты и безопасность.** Формализует schema, preconditions, side
  effects, timeout, idempotency, permissions, sandbox и approval gates.
- **Диагностика.** Разбирает код, конфигурацию, traces, метрики и результаты
  tool calls; отделяет evidence от inference и unknowns.
- **Evals.** Строит baseline, representative и adversarial cases, holdout,
  метрики результата и trajectory, повторные прогоны, release gate, canary и
  rollback.
- **Специализированные архитектуры.** Покрывает coding agents, externalized
  learning, realtime voice/multimodal systems и multi-agent coordination.

## Как проходит работа

После вызова skill автономно:

1. изучает доступные требования, код, конфигурацию, traces и ограничения;
2. локализует задачу по модели, контексту, инструментам и Harness;
3. выбирает минимальную архитектуру и фиксирует failure paths;
4. предлагает порядок реализации короткими vertical slices с тестами;
5. определяет baseline, eval design, метрики, release gate и rollback.

Результат начинается с решения или диагноза, а не с общего обзора. Для
применённых принципов skill приводит точные ссылки на строки книги. Если данных
недостаточно, он формулирует instrumentation plan и эксперимент вместо
неподтверждённого вывода.

## Когда использовать

- спроектировать нового AI-агента или выбрать между workflow и agent loop;
- провести architecture review существующей агентной системы;
- найти причину повторных tool calls, потери контекста или неустойчивого
  восстановления;
- определить контракт инструментов, memory/RAG или self-improvement pipeline;
- проверить, улучшил ли результат новый prompt, model, tool или Harness;
- сравнить realtime или single-agent/multi-agent архитектуры при равном budget.

Для обычного приложения без агентного цикла и внешних действий этот skill не
нужен.

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

Прямой вызов в Codex:

```text
Используй $developing-ai-agents, чтобы спроектировать агента для моей задачи.
```

В Claude Code skill также доступен как команда:

```text
/developing-ai-agents:developing-ai-agents Спроектируй агента для моей задачи.
```

Примеры задач:

```text
Выбери минимальную архитектуру агента для этого продукта и объясни границу автономности.
Проведи review Harness: контекст, tools, constraints, verification и recovery.
Разбери trace и найди подтверждённую причину повторных вызовов инструмента.
Составь evals с baseline, holdout, adversarial cases и release gate.
Спроектируй безопасный pipeline externalized learning с provenance и rollback.
Сравни single-agent и multi-agent при одинаковом token/tool/time budget.
```

Прямой вызов необязателен: задачу можно сформулировать обычным текстом. Skill
рассчитан на проектирование, review, отладку и оценку агентных систем.

## Состав

- `SKILL.md` — ядро и маршрут по задаче: тип запроса → стартовый файл.
- `references/playbooks/` — семь пошаговых процедур: проектирование, разбор
  trace, review, evals, память, бюджет задержки, выбор multi-agent.
- `references/templates/` — шесть заполняемых артефактов с примерами.
- `references/chapters/` — двенадцать конспектов глав книги с проверенными
  цитатами.
- `references/patterns.md` — шестнадцать паттернов «failure mode → механизм →
  проверка»; `references/antipatterns.md` — каталог ошибок по симптомам.
- `references/source-book/` — русский текст книги; `references/source-map.md` и
  `references/source-map.lock.json` — карта тем и фиксация якорей.
- `plugins/developing-ai-agents/evals/` — быстрый набор, benchmark v2 и v3,
  триггер-набор из 36 запросов.
- `scripts/validate.py`, `scripts/build_source_lock.py` — проверки и генератор
  lock-файла.

## Проверка

```bash
python3 scripts/build_source_lock.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
claude plugin validate plugins/developing-ai-agents --strict
```

## Проверка достоверности

Каждое утверждение конспектов, приписанное книге, проверяется машинно —
`scripts/validate.py` падает в CI при расхождении.

1. **Lock якорей.** `references/source-map.lock.json` хранит sha256 строки
   книги для каждого якоря. Любой сдвиг текста обнаруживается; валидатор не
   обновляет lock самостоятельно, чтобы расхождение попадало в diff.
2. **Якорь указывает на заголовок.** Ссылка в середину абзаца хрупка и
   непроверяема; исключения перечисляются в lock с указанием причины.
3. **Дословная цитата внутри секции якоря.** Цитата ищется от заголовка до
   следующего заголовка любого уровня — цитата из соседнего подраздела
   отклоняется. Дополнительно сверяется число начатых и разобранных цитат:
   нераспознанная цитата опаснее неверной, поскольку выглядит подтверждённой.

Сверх этого проверяются лимит `SKILL.md` в 300 строк, полнота маршрута (файл,
не упомянутый в `SKILL.md`, агент не найдёт) и покрытие каждого playbook
сценариями бенчмарка.

Обновление lock после правки якорей:

```bash
python3 scripts/build_source_lock.py
```

## Результаты evals

### v2: со скиллом против без скилла

12 сценариев, по три запуска на конфигурацию.

| Метрика | С навыком | Без навыка |
|---|---:|---:|
| Выполненные требования | 90,0% (162/180) | 75,0% (135/180) |
| Победы в слепом сравнении | 28/36 | 8/36 |

Модель запуска, расход токенов и время не записывались. Задачи внутри одного
контекста запуска не были полностью независимы. Данные:
[`benchmarks/v2/`](plugins/developing-ai-agents/benchmarks/v2/).

### v3: сравнение версий

32 сценария. Слепая парная оценка использовалась для поиска регрессий при
переносе материала из ядра в справочные слои; найденные расхождения устранены.

Шесть сценариев требуют заполненного артефакта — это прямая проверка слоя
шаблонов: 30/30 закрытых полей против 25/30 у версии без шаблонов, расхождения
5:0 в одну сторону.

### Триггеринг

| Метрика | Значение |
|---|---:|
| Срабатывание на целевых запросах | 18/18 |
| Ложные срабатывания | 1/18 |

Измерено на установленном плагине: `python3 scripts/measure_triggering.py`.

Сырые оценки, метод и ограничения прогонов —
[`benchmarks/v3/`](plugins/developing-ai-agents/benchmarks/v3/).

## Автор книги и исходные материалы

- Автор: [Bojie Li](https://github.com/bojieli).
- Оригинал: [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book).
- Русский перевод: [ilkruglov/ai-agent-book](https://github.com/ilkruglov/ai-agent-book),
  «Русский перевод: community edition».

Версии исходных материалов указаны в [`SOURCE.json`](SOURCE.json). Уведомление
об авторстве находится в [`NOTICE`](NOTICE).

## Лицензия

Apache License 2.0. См. [`LICENSE`](LICENSE).
