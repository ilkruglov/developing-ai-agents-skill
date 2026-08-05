# Глава 2. Инженерия контекста

## Основная идея

Контекст — не transcript, а управляемая рабочая среда модели. Его качество определяют релевантность, структура, стабильность, state visibility, lifecycle и связь с внешними артефактами. Большое context window не устраняет retrieval interference, забывание ограничений или неясное состояние.

Источники: `references/source-book/chapter2.md:9`, `references/source-book/chapter2.md:34`, `references/source-book/chapter2.md:355`.

## Framework: prefix, projection, trajectory

Раздели context API на:

- **stable prefix:** system policy и стабильные tool definitions;
- **task contract:** цель, acceptance criteria и неизменяемые ограничения;
- **state projection:** актуальный status, budget, decisions и artifacts;
- **selected memory/evidence:** только релевантные фрагменты с provenance;
- **trajectory:** недавние user/model/tool turns.

Стабильный prefix повышает KV/prompt-cache reuse и уменьшает instruction drift. Динамические данные не должны заставлять переписывать всё начало prompt. Tool descriptions — часть архитектуры и cache footprint.

Источники: `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:488`, `references/source-book/chapter2.md:518`, `references/source-book/chapter2.md:524`, `references/source-book/chapter2.md:635`.

## Agent Skills и progressive disclosure

Skill — модуль знаний/процесса, который загружается при релевантном запросе. Description должна позволять маршрутизатору выбрать skill, а основной файл — вести действие. Подробности лежат в references и загружаются только по необходимости. Это уменьшает постоянный context footprint и предотвращает смешение несовместимых процедур.

Источники: `references/source-book/chapter2.md:689`, `references/source-book/chapter2.md:700`, `references/source-book/chapter2.md:722`, `references/source-book/chapter2.md:745`.

## Agent Status Bar

Статус — компактная typed-проекция в конце контекста. Полезные поля: current objective, state version, active step, elapsed/deadline, remaining steps/tokens/cost, completed milestones, pending approvals, last verified artifact. Он помогает модели воспринимать физическое время и прогресс.

Status Bar не должен быть свободным текстом, который модель сама бесконтрольно переписывает. Авторитетное состояние обновляет controller/reducer; модель предлагает переход.

Источники: `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:777`, `references/source-book/chapter2.md:842`, `references/source-book/chapter2.md:856`, `references/source-book/chapter2.md:916`.

## Framework: progressive compression

Сжимай как можно позже и локальнее:

1. ограничь tool output, полный результат сохрани как artifact;
2. удали шум и повтор;
3. микро-сожми однотипные структуры;
4. архивируй завершённый этап в typed summary;
5. пересобери context из durable state как аварийный механизм.

Сохраняй decisions, constraints, changed files, test results, exact artifact IDs, pending work и rollback. Для независимых подзадач изоляция child context обычно лучше дальнейшего сжатия parent context.

Источники: `references/source-book/chapter2.md:936`, `references/source-book/chapter2.md:940`, `references/source-book/chapter2.md:981`, `references/source-book/chapter2.md:1017`, `references/source-book/chapter2.md:1029`, `references/source-book/chapter2.md:1054`.

## Security boundary

Недоверенный retrieved/tool/user content остаётся данными. Не позволяй ему незаметно изменить system policy или tool permissions. Отмечай provenance, ограничивай место вставки, отделяй инструкции от evidence и применяй enforcement вне prompt.

Источник: `references/source-book/chapter2.md:655`.

## Антипаттерны

- Добавлять каждое правило в system prompt навсегда.
- Хранить полный tool output inline.
- Сжимать всю историю одним свободным summary без schema.
- Менять ранний prefix на каждом turn ради clock/progress.
- Передавать child agent всю историю вместо task contract.
- Считать найденный фрагмент доверенной инструкцией.

## Рабочий пример и eval

Для Coding Agent, деградирующего через час:

1. измерь token composition и repeated-call trace;
2. вынеси state/event log из transcript;
3. введи stable prefix и Status Bar;
4. ограничь outputs и добавь progressive compression;
5. запускай независимые исследования в child contexts;
6. проведи forced-rollover/restart benchmark.

Success: constraint retention, task completion, lower repeat-call rate и меньшие tokens при неизменном внешнем outcome. Cache hit — полезная системная метрика, но не замена quality.
