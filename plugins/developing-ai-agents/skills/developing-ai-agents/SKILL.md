---
name: developing-ai-agents
description: Use when designing, implementing, reviewing, debugging, or evaluating an AI agent, especially for context engineering, tool interfaces, Harness reliability, memory, evaluation, self-evolution, realtime interaction, or multi-agent coordination. Do not use for ordinary non-agent application code.
---

# Разработка AI-агентов

Проектируй агента как проверяемую систему, а не как «промпт плюс мощная модель». Опирайся на русское издание книги Bojie Li «AI-агенты изнутри: принципы проектирования и инженерная практика» и на факты из текущего проекта.

## Рабочий контракт

1. Сначала изучи реальные требования, код, конфигурацию, трассы, метрики и ограничения. Не называй гипотезу причиной без доказательств.
2. Разделяй:
   - **evidence** — что подтверждено кодом, логом, тестом или измерением;
   - **inference** — наиболее вероятное объяснение;
   - **unknown** — что ещё нужно измерить.
3. Начинай ответ с решения или диагноза. После него дай минимальную архитектуру, порядок реализации, проверки и риски.
4. Для review или diagnosis оставайся read-only, пока пользователь явно не попросит изменить систему. Для реализации соблюдай инструкции репозитория и TDD.
5. Книжные принципы считай устойчивыми инженерными эвристиками. Актуальность моделей, SDK, API, протоколов, цен, лимитов и поддержки провайдеров проверяй по первичным текущим источникам.
6. По умолчанию укладывай архитектурный ответ в 1200 слов. Расширяй его только по явному запросу; если деталей больше, приоритизируй решения, contracts и проверки, а не полный checklist.

## Основная модель

Используй формулу:

> **AI-агент = LLM + контекст + инструменты**

- **LLM** принимает решения, но не хранит надёжное состояние системы.
- **Контекст** определяет, что агент видит сейчас: инструкции, состояние, историю и результаты действий.
- **Инструменты** превращают намерение в наблюдаемое действие во внешнем мире.
- **Harness** связывает три части в управляемый замкнутый контур.

При сбое сначала локализуй дефект по этим четырём областям. Не начинай с замены модели, пока не проверены context lifecycle, tool contract и Harness.

Источник: `references/source-book/chapter1.md:13`, `references/source-book/chapter1.md:146`, `references/source-book/chapter1.md:230`.

## Выбери минимальную архитектуру

Двигайся по лестнице сложности и остановись на первом варианте, который выполняет задачу:

1. **Один вызов модели** — задача одношаговая, без внешнего состояния и действий.
2. **Детерминированный workflow** — шаги известны заранее; модель заполняет ограниченные участки.
3. **Один автономный агент** — следующий шаг зависит от нового наблюдения или результата инструмента.
4. **Несколько агентов** — независимые роли получают новое внешнее свидетельство или реально параллелят независимую работу.

Не добавляй multi-agent только ради «дебатов»: повторная генерация над тем же контекстом часто увеличивает стоимость, задержку и коррелированные ошибки. Сравни multi-agent с single-agent при одинаковом token/tool/time budget.

Источники: `references/source-book/chapter1.md:295`, `references/source-book/chapter1.md:324`, `references/source-book/chapter10.md:65`.

## Спроектируй Harness

Проверь пять функций как один контур:

| Функция | Вопрос | Production-механизм |
|---|---|---|
| Context | Достаточно ли релевантной информации для следующего решения? | стабильный префикс, ограниченная траектория, явное состояние |
| Tools | Понятен ли модели контракт действия и результата? | узкие схемы, типы, идемпотентность, структурированные ошибки |
| Constraints | Что запрещено по умолчанию? | least privilege, allowlist, sandbox, лимиты, approval gates |
| Verification | Как результат проверяется независимо от заявления агента? | тест, schema, oracle, verifier, изолированный evaluator |
| Correction | Как система обнаруживает сбой, восстанавливается и не повторяет его? | retry policy, rollback, checkpoint, bounded loop, escalation |

Каждое действие должно оставлять проверяемое наблюдение, которое возвращается в контекст. Устанавливай `max_steps`, deadline, budget, cancellation и terminal states. Скрывай промежуточную ошибку от пользователя лишь пока существует ограниченный путь восстановления; затем сообщай точный blocker.

Источник: `references/source-book/chapter1.md:272-294`.

## Спроектируй context lifecycle

1. Отдели **стабильный префикс** от **динамической траектории**:
   - префикс: системные инструкции и стабильные tool definitions;
   - траектория: сообщения, tool calls/results и новые наблюдения.
2. Держи рабочее состояние явно: цель, принятые решения, ограничения, завершённые шаги, активный шаг, артефакты, тесты, риски и следующий шаг.
3. Не используй transcript одновременно как журнал, память и source of truth. Полный event log может жить вне prompt; в контекст попадает нужная проекция.
4. Применяй сжатие по уровням:
   1. ограничить объём tool output, сохранив полный артефакт вне контекста;
   2. удалить шум и дубликаты;
   3. микро-сжать повторяющиеся API/tool results;
   4. архивировать завершённые этапы в структурированное summary;
   5. полностью пересобрать контекст только как circuit breaker.
5. При сжатии всегда сохраняй решения, ограничения, изменённые файлы, результаты тестов, идентификаторы артефактов, незавершённую работу и rollback plan.
6. Для независимой подзадачи предпочитай изолированный дочерний контекст с узким входом и структурированным выходом. Не передавай ребёнку всю историю родителя.

Источники: `references/source-book/chapter2.md:355`, `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:936`, `references/source-book/chapter2.md:1017`, `references/source-book/chapter2.md:1054`.

## Спроектируй инструменты и безопасность

Для каждого инструмента зафиксируй:

- одну понятную capability и точную schema входа/выхода;
- preconditions, side effects, timeout, retry semantics и idempotency key;
- ошибки как данные: код, причина, retryable, remediation;
- provenance результата и связь с конкретным вызовом;
- read/write/network/secret permissions;
- sandbox и resource limits для недоверенного кода;
- human approval перед необратимыми или высокорисковыми действиями.

Выбирай специализированный tool для стабильной операции со строгим контрактом. Выбирай Skill + универсальный executor для меняющегося процесса, который требует рассуждения. Не превращай универсальный shell/browser в неограниченный capability.

Источники: `references/source-book/chapter4.md:14`, `references/source-book/chapter4.md:41`, `references/source-book/chapter4.md:347`, `references/source-book/chapter8.md:187`, `references/source-book/chapter8.md:236`, `references/source-book/chapter8.md:329`.

## Спроектируй память и самоулучшение

Для запроса о самообучении/самоулучшении **явно сопоставь в ответе все три механизма**, прежде чем выбрать один:

1. **Post-training** изменяет веса и требует тренировочного контура.
2. **In-context learning** действует только в текущем контексте.
3. **Externalized learning** сохраняет опыт во внешних, версионируемых носителях без изменения весов.

Для безопасной первой версии предпочитай externalized learning:

- факты и подтверждённые знания → knowledge base;
- повторяемая параметризуемая операция → code/tool;
- меняющийся стратегический процесс → Skill;
- пользовательское состояние → отдельная typed memory с provenance и retention policy.

Не превращай сырой лог или единичную неудачу в правило. Проводи цепочку `episode → extraction → candidate → review/eval → promotion`. Храни origin, supporting episodes, confidence, version, scope и rollback. Для новых инструментов используй `discover → inspect provenance → sandbox test → permission review → canary → promote`; опасные capability требуют approval.

Источники: `references/source-book/chapter3.md:49`, `references/source-book/chapter3.md:94`, `references/source-book/chapter8.md:23`, `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`, `references/source-book/chapter8.md:113`, `references/source-book/chapter8.md:319`.

## Построй eval-loop до оптимизации

1. Зафиксируй baseline и версии модели, prompt, tools, data и среды.
2. Собери задачи из реального распределения, граничные случаи и adversarial cases. Отдели development set от holdout.
3. Используй внешне проверяемый outcome, а не самооценку агента. Где точного oracle нет, применяй rubric, pairwise evaluation и blinded judge; калибруй judge на человеческой выборке.
4. Измеряй минимум:
   - task success;
   - constraint/safety violations;
   - ошибки выбора/вызова инструментов и trajectory;
   - latency, tokens, cost и число шагов;
   - recovery, повторяемость и каскадные ошибки.
5. Меняй один механизм за раз или проводи ablation. Для стохастической системы используй повторные прогоны, confidence intervals и заранее заданный release gate.
6. Выпускай через shadow/canary, сохраняй rollback и отслеживай drift после релиза.

Если данных ещё нет, дай instrumentation plan и эксперимент; не заявляй улучшение заранее.

Источники: `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:157`, `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:284`, `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:534`, `references/source-book/chapter6.md:563`, `references/source-book/chapter6.md:635`.

## Realtime и multi-agent

Для запроса о выборе голосовой архитектуры **явно сравни в ответе все три парадигмы**, даже если одна быстро исключается:

- **Cascading**: streaming ASR → LLM/agent → streaming TTS; проще контролировать и измерять, хороший v1.
- **Omni**: единая модель воспринимает/порождает несколько модальностей; меньше интерфейсных потерь, но сложнее наблюдаемость и контроль.
- **Full-Duplex**: одновременное восприятие и выражение, barge-in и непрерывное управление; максимальная естественность и максимальная сложность гонок.

После сравнения задай измеримый latency budget. Если product SLA неизвестен, объяви конкретный provisional budget гипотезой (не отраслевым фактом), разложи его по стадиям и укажи, какими p50/p95 traces он будет откалиброван.

Раздели fast interaction loop и slow reasoning. Передавай `turn_id`, snapshot/version состояния, deadline, cancellation token, confidence и structured result. Устаревший результат не должен озвучиваться и не должен продолжать side effects.

Для multi-agent зафиксируй две оси:

- shared context или isolated contexts;
- peer, manager или decentralized topology.

Разделяй data plane (файлы, артефакты, версии, ownership) и control plane (задачи, сообщения, heartbeat, cancellation). Для shared filesystem используй ownership/worktrees/optimistic locking. Независимый verifier должен читать исходное evidence, а не пересказ proposer-а.

В сравнении single-agent/multi-agent отдельно проверяй каскадные ошибки: внедри правдоподобное неверное upstream evidence/заключение и измерь, сколько ролей его принимает, усиливает и передаёт дальше (`false_accept`, `cascade_depth`, итоговый вред). `handoff failure` не заменяет эту проверку.

Источники: `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:42`, `references/source-book/chapter9.md:149`, `references/source-book/chapter9.md:174`, `references/source-book/chapter9.md:192`, `references/source-book/chapter10.md:11`, `references/source-book/chapter10.md:15`, `references/source-book/chapter10.md:53`, `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`, `references/source-book/chapter10.md:481`.

## Формат результата

Адаптируй глубину к запросу, но по умолчанию выдай:

1. **Решение** — минимальный выбранный вариант и что не делать сейчас.
2. **Evidence / unknowns** — подтверждённые факты и пробелы.
3. **Архитектура** — компоненты, состояние, контракты и failure paths.
4. **Порядок реализации** — тонкие vertical slices с тестами.
5. **Доказательство эффекта** — baseline, eval design, метрики и release gate.
6. **Риски и rollback**.
7. **Источники книги** — точные `references/source-book/*.md:line`; только для реально применённых идей.

Не перегружай ответ универсальным checklist и не повторяй один механизм в нескольких разделах. Привязывай каждый механизм к наблюдаемому failure mode и проверке. По умолчанию держи результат не длиннее 1200 слов.

## Навигация по материалам

- Быстрый выбор архитектуры и проверок: [references/cheatsheet.md](references/cheatsheet.md)
- Сквозные шаблоны: [references/patterns.md](references/patterns.md)
- Каталог ошибок по симптомам: [references/antipatterns.md](references/antipatterns.md)

Пошаговые процедуры под типовые задачи:

| Задача | Playbook |
|---|---|
| Спроектировать агента с нуля | [references/playbooks/design-agent.md](references/playbooks/design-agent.md) |
| Разобрать trace и найти причину | [references/playbooks/diagnose-trace.md](references/playbooks/diagnose-trace.md) |
| Провести review существующей системы | [references/playbooks/harness-review.md](references/playbooks/harness-review.md) |
| Построить или починить evals | [references/playbooks/build-evals.md](references/playbooks/build-evals.md) |
| Спроектировать память и самоулучшение | [references/playbooks/memory-design.md](references/playbooks/memory-design.md) |
| Задать бюджет задержки для realtime | [references/playbooks/realtime-latency.md](references/playbooks/realtime-latency.md) |
| Решить, нужно ли несколько агентов | [references/playbooks/multi-agent-choice.md](references/playbooks/multi-agent-choice.md) |

Заполняемые артефакты:

| Артефакт | Шаблон |
|---|---|
| Проект агента | [references/templates/agent-design.md](references/templates/agent-design.md) |
| Спецификация Harness | [references/templates/harness-spec.md](references/templates/harness-spec.md) |
| Контракт инструмента | [references/templates/tool-contract.md](references/templates/tool-contract.md) |
| План оценки | [references/templates/eval-plan.md](references/templates/eval-plan.md) |
| Политика памяти | [references/templates/memory-policy.md](references/templates/memory-policy.md) |
| Разбор trace | [references/templates/trace-diagnosis.md](references/templates/trace-diagnosis.md) |
- Термины: [references/glossary.md](references/glossary.md)
- Точная карта источников: [references/source-map.md](references/source-map.md)

Конспекты глав — читай тот, который относится к задаче:

| Тема | Файл |
|---|---|
| Назначение и структура книги | [references/chapters/ch00-introduction.md](references/chapters/ch00-introduction.md) |
| Формула агента, ReAct, Harness | [references/chapters/ch01-agent-foundations.md](references/chapters/ch01-agent-foundations.md) |
| Контекст, кэш, сжатие, Status Bar | [references/chapters/ch02-context-engineering.md](references/chapters/ch02-context-engineering.md) |
| Память, RAG, retrieval | [references/chapters/ch03-memory-and-knowledge.md](references/chapters/ch03-memory-and-knowledge.md) |
| Инструменты, MCP, async | [references/chapters/ch04-tools.md](references/chapters/ch04-tools.md) |
| Coding agents, recovery | [references/chapters/ch05-coding-agents.md](references/chapters/ch05-coding-agents.md) |
| Evals, метрики, judge | [references/chapters/ch06-evaluation.md](references/chapters/ch06-evaluation.md) |
| Post-training, SFT, RL | [references/chapters/ch07-post-training.md](references/chapters/ch07-post-training.md) |
| Самоулучшение, Skills, tool creation | [references/chapters/ch08-self-evolution.md](references/chapters/ch08-self-evolution.md) |
| Realtime, голос, мультимодальность | [references/chapters/ch09-realtime-multimodal.md](references/chapters/ch09-realtime-multimodal.md) |
| Multi-agent, топологии, каскады | [references/chapters/ch10-multi-agent.md](references/chapters/ch10-multi-agent.md) |
| Возврат к основной формуле | [references/chapters/ch11-afterword.md](references/chapters/ch11-afterword.md) |

Загружай только релевантные reference-файлы. Не помещай всю книгу в контекст одновременно.
