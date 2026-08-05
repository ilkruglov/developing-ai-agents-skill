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

## С чего начать: маршрут по задаче

| Запрос выглядит как | Начни с | Добери при необходимости |
|---|---|---|
| спроектировать агента с нуля | [playbooks/design-agent.md](references/playbooks/design-agent.md) | [templates/agent-design.md](references/templates/agent-design.md), [patterns.md](references/patterns.md) |
| разобрать trace, найти причину сбоя | [playbooks/diagnose-trace.md](references/playbooks/diagnose-trace.md) | [templates/trace-diagnosis.md](references/templates/trace-diagnosis.md), [antipatterns.md](references/antipatterns.md) |
| review существующей агентной системы | [playbooks/harness-review.md](references/playbooks/harness-review.md) | [templates/harness-spec.md](references/templates/harness-spec.md) |
| построить или починить evals | [playbooks/build-evals.md](references/playbooks/build-evals.md) | [templates/eval-plan.md](references/templates/eval-plan.md) |
| память, RAG, самоулучшение | [playbooks/memory-design.md](references/playbooks/memory-design.md) | [templates/memory-policy.md](references/templates/memory-policy.md) |
| голос, realtime, мультимодальность | [playbooks/realtime-latency.md](references/playbooks/realtime-latency.md) | [chapters/ch09](references/chapters/ch09-realtime-multimodal.md) |
| один агент или несколько | [playbooks/multi-agent-choice.md](references/playbooks/multi-agent-choice.md) | [chapters/ch10](references/chapters/ch10-multi-agent.md) |
| контракт инструмента, права, песочница | [templates/tool-contract.md](references/templates/tool-contract.md) | [chapters/ch04](references/chapters/ch04-tools.md) |
| симптом известен, причина нет | [antipatterns.md](references/antipatterns.md) | playbook по нужной области |
| что говорит книга по теме | [source-map.md](references/source-map.md) | нужный конспект главы |

Загружай только релевантные файлы. Не помещай всю книгу в контекст одновременно.

## Основная модель

> **AI-агент = LLM + контекст + инструменты**

- **LLM** принимает решения, но не хранит надёжное состояние системы.
- **Контекст** определяет, что агент видит сейчас: инструкции, состояние, историю и результаты действий; определения инструментов входят сюда же и занимают тот же бюджет.
- **Инструменты** превращают намерение в наблюдаемое действие во внешнем мире.
- **Harness** связывает три части в управляемый замкнутый контур.

При сбое сначала локализуй дефект по этим четырём областям. Не начинай с замены модели, пока не проверены context lifecycle, tool contract и Harness.

Источники: `references/source-book/chapter1.md:13`, `references/source-book/chapter1.md:146`, `references/source-book/chapter1.md:230`.

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

Подробно: [chapters/ch01](references/chapters/ch01-agent-foundations.md). Источник: `references/source-book/chapter1.md:272-294`.

## Надёжность: сбои, повторы, восстановление

Классифицируй сбой до того, как считать попытки. Первый вопрос — не «повторить ли», а «имеет ли повтор смысл».

| Уровень | Типичные сбои | Что делать |
|---|---|---|
| API | 429, перегрузка, таймаут, разрыв, обрезка вывода | незаметный повтор с задержкой |
| Инструменты | несуществующий инструмент, неверные параметры, одинаковая ошибка подряд | менять вызов; повтор без изменения бесполезен |
| Контекст | переполнение окна, неудачное сжатие, повреждённая траектория | пересборка из durable state |
| Поток управления | цикл без прогресса, спираль в самой логике recovery | предохранитель и эскалация |

Обязательные механизмы:

- **Неизвестный исход не равен неудаче.** После таймаута побочный эффект мог произойти. Переводи вызов в состояние `unknown`, сверяй фактическое состояние провайдера и только затем решай. Поздний результат применяй как versioned transition, а не как новый вызов.
- **Отпечаток вызова** по паре «инструмент + параметры» ловит цикл без прогресса, который счётчик попыток не видит.
- **Беззвучное зависание опаснее разрыва**: разрыв даёт ошибку, зависание — нет. Нужен мониторинг активности потока, а не только перехват исключений.
- **Эскалация с ростом видимости**: незаметный повтор → повтор с изменением → откат к устойчивому состоянию → сообщение пользователю → передача человеку. Уровень выше только после исчерпания нижнего.
- **Durable checkpoint** переживает рестарт и содержит: цель, ограничения, принятые решения, изменённые файлы, доказательства тестов, незавершённую работу, следующее действие и план отката. Возобновление начинается со сверки записи с фактическим состоянием.

Тесты надёжности покрывают: повторную и внеочередную доставку события, поздний успех после таймаута, аварийную остановку с последующим возобновлением, отмену до и после фиксации побочного эффекта.

Подробно: [chapters/ch05](references/chapters/ch05-coding-agents.md). Источники: `references/source-book/chapter5.md:233`, `references/source-book/chapter4.md:347`.

## Контекст

1. Отдели **стабильный префикс** (системные инструкции, tool definitions) от **динамической траектории**. Ничто изменяющееся каждый ход не живёт в префиксе: это ломает кэш и поднимает задержку.
2. Держи рабочее состояние явно и проецируй его в конец контекста: цель, решения, ограничения, активный шаг, артефакты, тесты, риски, следующий шаг.
3. Не используй transcript одновременно как журнал, память и source of truth.
4. Сжимай по уровням: ограничить вывод инструмента → удалить шум → микро-сжать однотипное → архивировать этап в typed summary → пересобрать контекст как circuit breaker.
5. При сжатии всегда сохраняй решения, ограничения, изменённые файлы, результаты тестов, идентификаторы артефактов, незавершённую работу и rollback plan.
6. Для независимой подзадачи предпочитай изолированный дочерний контекст: изоляция дешевле сжатия.

Подробно: [chapters/ch02](references/chapters/ch02-context-engineering.md). Источники: `references/source-book/chapter2.md:355`, `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:936`, `references/source-book/chapter2.md:1054`.

## Инструменты и безопасность

Для каждого инструмента зафиксируй: одну capability и точную schema; preconditions, side effects, timeout, retry semantics, idempotency key; ошибки как данные (код, причина, retryable, remediation); provenance результата; permissions; sandbox для недоверенного кода; human approval перед необратимым действием.

Описание инструмента отвечает на вопрос «когда применять», а не только «что умеет», и содержит контрпримеры — чего инструмент не делает.

Выбирай специализированный tool для стабильной операции со строгим контрактом; Skill + универсальный executor — для меняющегося процесса, требующего рассуждения. Не превращай универсальный shell/browser в неограниченный capability.

При росте числа инструментов до десятков выбор ухудшается, а кэш префикса перестаёт работать. Переходи к послойному раскрытию: сначала указатель, затем схема нужного инструмента — вместо полной выдачи всех схем сразу.

Инструмент, созданный агентом, до попадания в библиотеку проходит: проверку происхождения и зависимостей, запуск в песочнице без секретов, сети и записи по умолчанию, контрактные и adversarial тесты, review разрешений. Иначе ошибка распространится на все последующие задачи.

Недоверенный контент (веб-страницы, документы, результаты инструментов, записи памяти) остаётся данными: он не размещается там, где живут инструкции, и не влияет на права. Enforcement — вне промпта.

Подробно: [chapters/ch04](references/chapters/ch04-tools.md), [chapters/ch05](references/chapters/ch05-coding-agents.md). Источники: `references/source-book/chapter4.md:14`, `references/source-book/chapter4.md:41`, `references/source-book/chapter2.md:655`, `references/source-book/chapter8.md:329`.

## Память и самоулучшение

Для запроса о самообучении **явно сопоставь в ответе все три механизма**, прежде чем выбрать один:

1. **Post-training** изменяет веса и требует тренировочного контура и оценки.
2. **In-context learning** действует только в текущем контексте.
3. **Externalized learning** сохраняет опыт во внешних версионируемых носителях без изменения весов.

Для безопасной первой версии предпочитай externalized learning: факты → knowledge base; повторяемая параметризуемая операция → code/tool; меняющийся процесс → Skill; пользовательское состояние → typed memory с provenance и retention policy.

Постобучение рассматривай только после исправления интерфейса и контекста: если после этого остаётся нестабильность формата на распределении задач, SFT на чистых демонстрациях с отдельным holdout — рабочий вариант. RL нужен там, где среда развёртывания отличается от демонстраций.

Не превращай сырой лог или единичную неудачу в правило. Проводи цепочку `episode → extraction → candidate → review/eval → promotion` и храни origin, supporting episodes, confidence, version, scope и rollback. Запись в память проходит ту же проверку доверия, что и внешний ввод, иначе инъекция переживёт сессию.

Подробно: [chapters/ch03](references/chapters/ch03-memory-and-knowledge.md), [chapters/ch08](references/chapters/ch08-self-evolution.md), [chapters/ch07](references/chapters/ch07-post-training.md). Источники: `references/source-book/chapter3.md:49`, `references/source-book/chapter8.md:23`, `references/source-book/chapter8.md:319`.

## Построй eval-loop до оптимизации

1. Зафиксируй baseline и версии модели, prompt, tools, data и среды.
2. Собери задачи из реального распределения, граничные и adversarial случаи. Отдели development set от holdout и не тюнись на holdout.
3. Используй внешне проверяемый outcome, а не самооценку агента. Где точного oracle нет — rubric с весами, ловушками и вето, pairwise evaluation, blinded judge, калибровка на человеческой выборке.
4. Измеряй минимум: task success (различая Pass@k и Pass^k), constraint violations отдельной метрикой, ошибки выбора и вызова инструментов, latency/tokens/cost, recovery и каскадные ошибки.
5. Меняй один механизм за раз или проводи ablation; переключатели абляции закладывай до фиксации конфигурации в коде.
6. Для стохастической системы измерь границу шума повторными прогонами: разница меньше неё решением не является. При сравнении многих вариантов повышай порог.
7. Выпускай через shadow/canary, держи проверенный rollback, отслеживай drift после релиза.

Если данных ещё нет, дай instrumentation plan и эксперимент; не заявляй улучшение заранее.

Подробно: [chapters/ch06](references/chapters/ch06-evaluation.md). Источники: `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:563`.

## Realtime и multi-agent

Для запроса о голосовой архитектуре **явно сравни в ответе все три парадигмы**, даже если одна быстро исключается:

- **Cascading**: streaming ASR → LLM/agent → streaming TTS; проще контролировать и измерять, хороший v1.
- **Omni**: единая модель для нескольких модальностей; выигрыш в задержке, но не обязательно в точности.
- **Full-Duplex**: одновременное восприятие и выражение, barge-in; максимальная естественность и максимальная сложность гонок.

Задай измеримый latency budget, разложенный по стадиям. Если product SLA неизвестен, объяви конкретный provisional budget гипотезой (не отраслевым фактом) и укажи, какими p50/p95 traces он будет откалиброван. Раздели fast interaction loop и slow reasoning; передавай `turn_id`, версию состояния, deadline, cancellation и structured result. Устаревший результат не озвучивается и не продолжает side effects. Отмена — не одно действие: остановка генерации, остановка вывода, отмена инструмента, отказ от повтора необратимого эффекта, компенсация обратимого.

Race-тесты обязательны и покрывают: перебивание до фиксации побочного эффекта и после неё, приход медленного результата после смены хода, коррекцию частичного распознавания, потерю сети в середине потока, запрет на озвучивание устаревшего результата.

Для multi-agent зафиксируй две оси: shared или isolated contexts; peer, manager или decentralized topology. Раздели data plane (файлы, артефакты, версии, ownership) и control plane (задачи, сообщения, heartbeat, cancellation). Независимый verifier читает исходное evidence, а не пересказ proposer-а.

В сравнении single-agent и multi-agent отдельно проверяй каскадные ошибки: внедри правдоподобное неверное upstream evidence и измерь `false_accept`, `cascade_depth` и итоговый вред. `handoff failure` эту проверку не заменяет.

Подробно: [chapters/ch09](references/chapters/ch09-realtime-multimodal.md), [chapters/ch10](references/chapters/ch10-multi-agent.md). Источники: `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:192`, `references/source-book/chapter10.md:11`, `references/source-book/chapter10.md:481`.

## Формат результата

Начинай с вердикта или решения в первых строках — не с изложения контекста. Адаптируй глубину к запросу, но по умолчанию выдай:

1. **Решение** — минимальный выбранный вариант и что не делать сейчас.
2. **Evidence / inference / unknown** — подтверждённое, объяснение и неизмеренное; отдельно выдели то, что требует проверки по текущей документации провайдера и не может быть подтверждено книгой.
3. **Архитектура** — компоненты, состояние, контракты и failure paths.
4. **Порядок реализации** — тонкие vertical slices с тестами.
5. **Доказательство эффекта** — baseline, eval design, метрики и release gate.
6. **Риски и rollback**.
7. **Источники книги** — точные `references/source-book/*.md:line`; только для реально применённых идей.

Не перегружай ответ универсальным checklist и не повторяй один механизм в нескольких разделах. Привязывай каждый механизм к наблюдаемому failure mode и проверке. По умолчанию держи результат не длиннее 1200 слов.

## Все материалы

**Справочники:** [cheatsheet.md](references/cheatsheet.md) — быстрый выбор архитектуры и проверок · [patterns.md](references/patterns.md) — 16 паттернов «failure mode → механизм → проверка» · [antipatterns.md](references/antipatterns.md) — каталог ошибок по симптомам · [glossary.md](references/glossary.md) — термины · [source-map.md](references/source-map.md) — карта книги по темам.

**Конспекты глав:** [ch00 введение](references/chapters/ch00-introduction.md) · [ch01 основы, ReAct, Harness](references/chapters/ch01-agent-foundations.md) · [ch02 контекст, кэш, сжатие](references/chapters/ch02-context-engineering.md) · [ch03 память и RAG](references/chapters/ch03-memory-and-knowledge.md) · [ch04 инструменты и MCP](references/chapters/ch04-tools.md) · [ch05 coding-агенты и recovery](references/chapters/ch05-coding-agents.md) · [ch06 оценка](references/chapters/ch06-evaluation.md) · [ch07 постобучение](references/chapters/ch07-post-training.md) · [ch08 самоэволюция](references/chapters/ch08-self-evolution.md) · [ch09 realtime](references/chapters/ch09-realtime-multimodal.md) · [ch10 multi-agent](references/chapters/ch10-multi-agent.md) · [ch11 послесловие](references/chapters/ch11-afterword.md)

**Процедуры:** [design-agent](references/playbooks/design-agent.md) · [diagnose-trace](references/playbooks/diagnose-trace.md) · [harness-review](references/playbooks/harness-review.md) · [build-evals](references/playbooks/build-evals.md) · [memory-design](references/playbooks/memory-design.md) · [realtime-latency](references/playbooks/realtime-latency.md) · [multi-agent-choice](references/playbooks/multi-agent-choice.md)

**Артефакты:** [agent-design](references/templates/agent-design.md) · [harness-spec](references/templates/harness-spec.md) · [tool-contract](references/templates/tool-contract.md) · [eval-plan](references/templates/eval-plan.md) · [memory-policy](references/templates/memory-policy.md) · [trace-diagnosis](references/templates/trace-diagnosis.md)
