# Глоссарий

Термины приведены в том смысле, в котором они полезны при проектировании системы.

## A–H

**ACI (Agent–Computer Interface)** — интерфейс между агентом и вычислительной средой: tool schemas, наблюдения, ошибки, состояние и правила исполнения. Аналог HCI для модели. Качество ACI часто важнее дополнительной «умности» модели.

**Agent Status Bar** — компактный блок метаданных в конце контекста: время, budget, текущий state, прогресс и другие показания, помогающие модели управлять траекторией. Это проекция состояния, а не свободный дневник.

**Agentic RAG** — поиск, при котором агент сам выбирает стратегию и инструменты получения знаний, выполняет несколько запросов и проверяет результаты, вместо единственного фиксированного retrieval шага.

**Cascading voice architecture** — цепочка streaming ASR → текстовый agent/LLM → streaming TTS. Компоненты наблюдаемы и заменяемы, но ошибки и задержки складываются.

**Context engineering** — проектирование всего контекста: стабильных инструкций, tool definitions, текущего состояния, истории, evidence, памяти, сжатия и cache behavior. Шире prompt engineering.

**Context projection** — ограниченное представление durable state/event log, собранное специально для следующего model turn.

**Control plane** — координация исполнителей: постановка задач, сообщения, status, heartbeat, cancellation, deadlines и ownership.

**Data plane** — сами данные и артефакты работы: файлы, результаты tool calls, версии, логи, тестовые отчёты.

**Externalized learning** — устойчивое обучение без изменения весов модели: опыт превращается в memory, knowledge, Skills или tools с provenance/versioning.

**Full-Duplex / Interactive model** — realtime-модель, которая одновременно воспринимает и выражает, поддерживает barge-in и непрерывное управление turn-taking.

**Harness** — инженерная оболочка агента, реализующая context, tools, constraints, verification и correction как замкнутый контур.

## I–R

**In-context learning** — временная адаптация поведения на примерах и информации внутри текущего context window; после удаления контекста не сохраняется.

**Knowledge base** — внешнее хранилище предметных знаний с источниками, freshness и retrieval. Не смешивать с рабочим состоянием run или пользовательской памятью.

**KV-cache** — кэш промежуточных представлений префикса трансформера. Изменение ранних токенов лишает последующую часть reuse, поэтому стабильный prefix — архитектурное требование, а не косметическая оптимизация.

**LLM-as-a-Judge** — автоматическая оценка ответа другой моделью по rubric. Требует калибровки, ослепления, контроля position/verbosity/self-preference bias и выборочной человеческой проверки.

**MCP (Model Context Protocol)** — протокол предоставления агенту инструментов и ресурсов. Наличие интеграции не заменяет least privilege, selection policy и проверку результата.

**Memory poisoning** — попадание в долговременную память ложного, вредоносного или prompt-injected содержания, которое затем влияет на будущие сессии.

**Omni architecture** — сквозная мультимодальная модель, воспринимающая и генерирующая несколько модальностей без обязательного текстового интерфейса между ними.

**Post-training** — изменение весов после pretraining: SFT, preference optimization, RL и связанные подходы. Требует данных, среды, objective и отдельной валидации.

**Provenance** — происхождение факта, артефакта, памяти или tool result: источник, версия, время, вызов и преобразования.

**RAG (Retrieval-Augmented Generation)** — получение релевантных фрагментов внешней базы и передача их модели для grounded generation.

**ReAct** — цикл Reason → Act → Observe, в котором решение приводит к инструментальному действию, а новое наблюдение влияет на следующий шаг.

**RLVP (Reinforcement Learning with Verifiable Process constraints/penalty)** — подход главы 7: reward за результат сочетается с проверяемыми ограничениями/штрафами траектории. Практический вывод: outcome и допустимость процесса оцениваются раздельно.

## S–Z

**Sessionless architecture** — подход, в котором долговременное состояние и артефакты не зависят от одного непрерывного чата; новый execution episode восстанавливается из внешнего состояния.

**Skill** — загружаемый по необходимости пакет стратегических инструкций, workflows и reference-материалов. Хорош для меняющегося процесса, который требует reasoning; не заменяет строгий tool для стабильного действия.

**SFT (Supervised Fine-Tuning)** — обучение на целевых demonstrations методом next-token prediction. Передаёт стиль/поведение, но не даёт автоматически надёжного оптимизатора для long-horizon outcome.

**Stable prefix** — редко меняющаяся начальная часть контекста, прежде всего system instructions и tool definitions. Помогает cache reuse и уменьшает случайный дрейф инструкций.

**Trajectory** — динамическая последовательность user/model/tool сообщений и наблюдений в текущем run.

**Typed memory** — память с явной schema, scope, provenance, confidence, version и retention, а не неструктурированный append-only текст.

**Verifier** — независимый механизм проверки результата по первичному evidence: deterministic test/oracle, schema validator, simulation или отдельный evaluator. Пересказ proposer-а не является независимым evidence.

**Workflow** — заранее известный control flow. Модель может принимать локальные решения, но порядок и границы задаёт код.

## Русские рабочие термины

**Граница полномочий** — точный набор ресурсов и side effects, разрешённых tool/agent. Реализуется capability/permission model, а не только текстовой просьбой.

**Замкнутый контур** — решение → действие → внешнее наблюдение → проверка → обновление состояния → следующее решение.

**Каскадная ошибка** — ошибка одного агента или стадии, которую последующие участники принимают как факт и усиливают.

**Экстернализация** — перенос знания или процедуры из скрытого/временного состояния модели в проверяемый внешний носитель.

Источники терминов: `references/source-book/chapter1.md:13-229`, `references/source-book/chapter1.md:230-294`, `references/source-book/chapter2.md:401-559`, `references/source-book/chapter2.md:689-935`, `references/source-book/chapter3.md:273-701`, `references/source-book/chapter6.md:284-420`, `references/source-book/chapter8.md:23-355`, `references/source-book/chapter9.md:28-287`, `references/source-book/chapter10.md:11-533`.
