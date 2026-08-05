# Паттерны проектирования AI-агентов

Каждый паттерн связывает failure mode, механизм и способ проверки. Не применяй паттерн без наблюдаемой проблемы или требования: механизм без сопоставленного отказа — это стоимость без выгоды.

## Оглавление

| № | Паттерн | Решает |
|---|---|---|
| 1 | Bounded ReAct Harness | цикл действий без границ и наблюдений |
| 2 | Stable Prefix + Dynamic Projection | дорогие длинные сессии, потеря ограничений |
| 3 | Durable State, Ephemeral Episodes | потеря работы при рестарте |
| 4 | Progressive Context Reduction | раздувание контекста и деградация до предела окна |
| 5 | Capability-Gated Tool Gateway | неограниченные действия во внешнем мире |
| 6 | Tool/Skill/Knowledge Carrier Selection | знание положено не в тот носитель |
| 7 | Evidence-Gated Self-Improvement | опыт превращается в правила без проверки |
| 8 | Evaluation Flywheel | улучшения недоказуемы |
| 9 | Proposer–Verifier with Independent Evidence | самоподтверждение вместо проверки |
| 10 | Manager + Isolated Workers | параллельная работа с конфликтами |
| 11 | Fast/Slow Realtime Loop | реакция против глубины |
| 12 | Source-Grounded Recommendation | рекомендация без прослеживаемого основания |
| 13 | Grounded Retrieval Layer | извлечение не находит или находит не то |
| 14 | Sessionless Resumable Worker | состояние живёт только в процессе |
| 15 | Post-Training Decision Gate | веса меняют там, где хватило бы Harness |
| 16 | Untrusted Content Firewall | внешний контент управляет агентом |

## 1. Bounded ReAct Harness

**Когда:** следующий шаг зависит от результата внешнего действия.

**Сигналы:** агент выполняет действия, но не наблюдает их результат; нет верхней границы числа шагов; повторные одинаковые вызовы.

**Структура:**

```text
state_n + context projection
  -> decide(action | finish | escalate)
  -> policy gate
  -> execute tool
  -> observe external result
  -> verify
  -> reduce(state_n, event) = state_n+1
```

**Инварианты:**

- конечный набор action types;
- schema-validated model output;
- `max_steps`, deadline и cost budget;
- terminal states и невозможность молчаливого бесконечного retry;
- каждый side effect связан с `run_id`, `call_id` и idempotency key;
- reducer детерминирован или отдельно тестируется.

**Стоимость:** один дополнительный слой состояния и обязательная сериализация событий. Окупается на первом же сбое, требующем воспроизведения.

**Проверка:** scripted environment с успешной траекторией, retryable error, permanent error, repeated action, timeout, cancellation и ложным заявлением модели об успехе.

Источники: `references/source-book/chapter1.md:146`, `references/source-book/chapter1.md:230`, `references/source-book/chapter2.md:86`.

## 2. Stable Prefix + Dynamic Projection

**Когда:** длинные сессии дороги, теряют constraints или плохо используют prompt cache.

**Сигналы:** рост задержки до первого токена без роста нагрузки; падение доли попаданий в кэш; агент забывает ограничение, заданное в начале сессии.

**Структура:**

```text
[stable system policy]
[stable tool definitions]
[task contract]
[typed status]
[selected memory/evidence]
[bounded recent trajectory]
```

Стабильные инструкции не переписываются на каждом turn. Изменяемые progress/time/budget поля располагаются в отдельной status projection. Полный event log и крупные outputs остаются во внешнем storage.

**Антипаттерн:** постоянно перегенерировать system prompt вместе с текущим состоянием. Это создаёт instruction drift и инвалидирует ранний cache prefix.

**Стоимость:** требуется отдельный компонент, собирающий проекцию состояния, и дисциплина: любое новое поле сначала классифицируется как стабильное или изменяемое.

**Проверка:** prefix hash/cache-hit telemetry, token composition по секциям, forced rollover и восстановление всех constraints после нескольких циклов сжатия.

Источники: `references/source-book/chapter2.md:355`, `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:887`.

## 3. Durable State, Ephemeral Episodes

**Когда:** Coding Agent работает долго, должен переживать restart или продолжать задачу между сессиями.

**Сигналы:** после перезапуска агент начинает заново; ход работы восстанавливается только чтением всей истории; неясно, какие изменения уже применены.

**Структура:** durable state хранит цель, decisions, constraints, progress, artifacts, test evidence, pending risks и next action. Новый episode получает компактную проекцию и последние релевантные events.

**Правило:** transcript — доказательный журнал, но не единственный source of truth. Обновление состояния имеет version/compare-and-swap или transactional boundary.

**Стоимость:** схема состояния становится публичным контрактом и требует миграций при изменении.

**Проверка:** принудительно остановить run на нескольких этапах; восстановить его в новом процессе; сравнить итог и соблюдение constraints с непрерывным baseline.

Источники: `references/source-book/chapter2.md:763-935`, `references/source-book/chapter5.md:82`, `references/source-book/chapter5.md:233`, `references/source-book/chapter8.md:181`.

## 4. Progressive Context Reduction

**Когда:** контекст раздувается или retrieval ухудшается задолго до жёсткого token limit.

**Сигналы:** качество падает при заполнении окна на 40–60%; агент повторяет уже сделанное; выводы инструментов занимают большую часть контекста.

**Уровни:**

1. full tool output → external artifact + bounded excerpt;
2. noise/duplicate deletion;
3. micro-compression повторяющихся result structures;
4. typed archival summary завершённой фазы;
5. full reconstruction из durable state как circuit breaker.

Независимую задачу лучше вынести в child context, чем сжимать всё для одного гигантского контекста.

**Стоимость:** каждый уровень — отдельный код с собственными тестами; неверное сжатие теряет решения молча.

**Проверка:** gold facts/constraints seeded в ранних шагах; после каждого уровня агент должен воспроизвести и применить их. Измеряй не только tokens, но task success, cache reuse и repeated actions.

Источники: `references/source-book/chapter2.md:936-1061`.

## 5. Capability-Gated Tool Gateway

**Когда:** агент читает/изменяет внешние системы, запускает код или использует сеть.

**Сигналы:** инструмент способен на необратимое действие без подтверждения; права выданы «на всякий случай»; нет журнала происхождения результата.

**Структура:** model предлагает typed intent; policy layer сверяет identity, scope и risk; executor получает только минимальный capability token; result normalizer возвращает structured observation; audit log сохраняет provenance.

```text
model intent -> schema -> policy -> approval? -> sandboxed executor
             <- structured result + provenance <-
```

**Risk classes:**

- read-only, ограниченный scope;
- reversible write;
- external communication/financial/security-sensitive action;
- irreversible/destructive action.

Последние два класса требуют явного gate; текстовый system prompt сам по себе не является enforcement.

**Стоимость:** дополнительная задержка на policy-проверке и работа по классификации каждого инструмента.

**Проверка:** prompt injection, path/scope escape, secret exfiltration, network egress, duplicate request, timeout, partial side effect, forged tool result.

Источники: `references/source-book/chapter1.md:387`, `references/source-book/chapter4.md:41`, `references/source-book/chapter4.md:179`, `references/source-book/chapter4.md:415`, `references/source-book/chapter8.md:329`.

## 6. Tool/Skill/Knowledge Carrier Selection

**Когда:** появляется новая повторяемая capability.

**Сигналы:** бизнес-правило живёт только в системном промпте; скрипт сохранён как заметка в памяти; один и тот же процесс описан в трёх местах по-разному.

| Нужда | Носитель |
|---|---|
| Найти подтверждённый факт | knowledge base/RAG |
| Выполнить стабильную параметризуемую операцию | code/tool |
| Следовать меняющейся стратегии с reasoning | Skill |
| Запомнить состояние конкретного пользователя | typed user memory |
| Изменить базовое поведение на распределении задач | post-training |

**Антипаттерны:** помещать бизнес-правило только в prompt, сохранять скрипт как неструктурированный memory item, превращать единичный log в глобальный Skill.

**Стоимость:** каждый носитель требует собственного жизненного цикла: версия, провенанс, удаление.

**Проверка:** carrier должен иметь schema/version/provenance, isolated test и lifecycle удаления/rollback.

Источники: `references/source-book/chapter3.md:94`, `references/source-book/chapter4.md:43`, `references/source-book/chapter8.md:113`, `references/source-book/chapter8.md:319`.

## 7. Evidence-Gated Self-Improvement

**Когда:** агент должен учиться на выполненных задачах без постоянного fine-tuning.

**Сигналы:** правила появляются после единичных случаев; неизвестно, откуда взялось правило; откатить изменение невозможно.

```text
episode (immutable)
 -> redact + classify outcome
 -> extract reusable candidate
 -> link supporting and contradicting evidence
 -> deduplicate + scope
 -> offline eval/ablation
 -> approval
 -> canary
 -> promote | rollback
```

Candidate имеет `candidate_id`, type, version, source episodes, scope, expiry/freshness, risk class и expected metric impact. Неудача может породить гипотезу, но не автоматически правило. Защищай extraction от инструкций внутри недоверенного content.

**Стоимость:** конвейер продвижения — отдельная подсистема с собственными хранилищем и оценкой.

**Проверка:** hidden holdout, temporal split, poisoned episodes, conflicting experiences, stale tool version, deletion request и transitive rollback всех derived artifacts.

Источники: `references/source-book/chapter8.md:23`, `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`, `references/source-book/chapter8.md:127`, `references/source-book/chapter8.md:145`, `references/source-book/chapter8.md:319`, `references/source-book/chapter8.md:329`.

## 8. Evaluation Flywheel

**Когда:** до первой оптимизации и после каждого изменения агента.

**Сигналы:** улучшения описываются словами, а не числами; изменения вносятся пачками; неизвестно, что сломалось после релиза.

```text
production traces -> taxonomy -> representative tasks
       -> baseline/variant runs -> external grading
       -> failure clusters -> one hypothesis -> one change
       -> ablation -> release gate -> canary telemetry
       -> new traces
```

**Design rules:**

- pin model/prompt/tool/data/environment versions;
- isolate dev, holdout and adversarial sets;
- compare equal budgets or report budget difference explicitly;
- evaluate outcome and trajectory separately;
- repeat stochastic runs and report uncertainty;
- do not tune on holdout failures;
- calibrate LLM judges against humans and deterministic checks.

**Стоимость:** поддержание стенда и наборов — постоянная работа, а не разовая настройка.

**Проверка:** reproduce baseline; force one known failure; ensure metric detects it; test rollback before release.

Источники: `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:157`, `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:563`, `references/source-book/chapter6.md:635`.

## 9. Proposer–Verifier with Independent Evidence

**Когда:** результат важен, а deterministic oracle неполон; второй исполнитель может независимо проверить первичные данные.

**Сигналы:** проверяющий соглашается почти всегда; обе роли видят один и тот же текст; отказ проверяющего не меняет поведение предлагающего.

Proposer отдаёт claim + artifact + evidence pointers. Verifier получает task contract и первичные artifacts, но не chain-of-thought и не авторитетный «правильный ответ» proposer-а. Verifier должен иметь возможность вернуть `pass`, `fail` или `unknown` с evidence.

Модели предлагающего и проверяющего берутся из разных семейств при сопоставимом уровне: одинаковые модели повторяют одинаковые ошибки. Базовые правила у них совпадают, а приоритеты различаются — предлагающий ориентирован на выполнение, проверяющий на риск. Причина отказа возвращается в траекторию как результат вызова инструмента, иначе предлагающий повторит то же самое.

**Не применять:** обе роли видят один текст, не используют tools/evidence и лишь голосуют. Это self-consistency/best-of-N, а не независимая проверка.

**Стоимость:** удвоение стоимости шага и рост задержки; оправдано только для необратимых или дорогих действий.

**Проверка:** inject plausible wrong proposal; verifier обязан обнаружить его по source/test. Измерь correlated error rate и false accept.

Источники: `references/source-book/chapter4.md:179`, `references/source-book/chapter6.md:278-420`, `references/source-book/chapter10.md:65`, `references/source-book/chapter10.md:251`.

## 10. Manager + Isolated Workers

**Когда:** задача распадается на независимые bounded subtasks и выигрывает от параллельной работы.

**Сигналы:** пять и более подзадач с зависимостями; агенты конкурируют за одни файлы; сбой одного портит работу остальных.

Manager создаёт contract: objective, allowed scope, inputs, expected artifact schema, budget и acceptance test. Worker получает минимальный context и владеет отдельным artifact/worktree. Manager объединяет результаты по schema и запускает общую интеграционную проверку.

Рабочая область делится на роли: приватный scratchpad воркера, общее пространство результатов, смонтированные внешние ресурсы и системные ресурсы только для чтения. Черновик одного воркера не должен становиться входом другого.

**Failure controls:** lease/heartbeat, timeout, cancellation, no overlapping ownership, immutable handoff, merge conflict policy, bounded retry и circuit breaker при повторяющемся blocker.

**Стоимость:** менеджер становится узким местом и точкой отказа; при росте числа воркеров требуется децентрализация.

**Проверка:** lost worker, duplicate completion, stale handoff, conflicting writes, wrong manager synthesis и cascading error.

Источники: `references/source-book/chapter2.md:1054`, `references/source-book/chapter10.md:196`, `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`, `references/source-book/chapter10.md:287`, `references/source-book/chapter10.md:481`.

## 11. Fast/Slow Realtime Loop

**Когда:** интерфейс должен реагировать быстрее, чем выполняется полное рассуждение.

**Сигналы:** пауза перед ответом ощущается пользователем; перебивание не останавливает речь; ответ приходит после смены темы.

Fast path отвечает за turn-taking, acknowledgement, короткие безопасные ответы и barge-in. Slow path работает с versioned snapshot, выполняет reasoning/tools и возвращает structured result. Dispatcher публикует результат только если `turn_id` и `state_version` актуальны.

Медленный контур должен отменяться, когда быстрый уже дал верный ответ: иначе система тратит секунды и деньги на повторение того же самого.

Cancellation разделяй:

- остановить generation;
- остановить TTS/вывод;
- отменить tool, если он cancellable;
- не повторять необратимый side effect;
- компенсировать уже выполненный reversible side effect.

**Стоимость:** два контура означают два набора состояний и явный протокол между ними.

**Проверка:** partial ASR correction, пользователь перебил до/после tool call, slow result пришёл после нового turn, TTS уже начал воспроизведение, сеть потеряна в середине stream.

Источники: `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:94`, `references/source-book/chapter9.md:174`, `references/source-book/chapter9.md:192`, `references/source-book/chapter9.md:276`.

## 12. Source-Grounded Recommendation

**Когда:** решение должно быть проверяемо и связано с книгой.

**Сигналы:** рекомендация звучит убедительно, но её нельзя опровергнуть; ссылка на принцип используется как подтверждение факта о провайдере.

Для каждого важного вывода укажи:

1. project evidence — код/trace/metric;
2. применённый принцип — точный `references/source-book/*.md:line`;
3. inference — почему принцип подходит к этому failure mode;
4. falsification test — что могло бы опровергнуть решение.

Книжная ссылка не подтверждает текущий provider fact. Для моделей/API/цен используй актуальную первичную документацию и дату проверки.

## 13. Grounded Retrieval Layer

**Когда:** агент отвечает на основе внешней базы знаний, и качество ответа определяется качеством извлечения.

**Сигналы:** документ существует, но не находится по точному коду ошибки; найденный фрагмент формально релевантен, но бесполезен вне контекста документа; один поиск на сложный вопрос.

**Структура:**

```text
запрос -> [плотный поиск | разреженный поиск] -> объединение
      -> переранжирование -> фрагменты с provenance
      -> агент решает: ответить | искать снова
```

**Инварианты:**

- разреженная составляющая обязательна там, где встречаются идентификаторы, коды и точные названия;
- фрагмент несёт сводку-префикс, добавленную при индексировании, иначе он теряет смысл вне документа;
- каждый фрагмент возвращается с provenance: источник, версия, дата;
- поиск оформлен как инструмент, а не как обязательный предварительный этап, чтобы агент мог уточнить запрос;
- пустая выдача — валидный результат, требующий явной обработки, а не молчаливого перехода к генерации.

**Стоимость:** два индекса вместо одного, переранжирование на каждый запрос, генерация префиксов при индексировании.

**Проверка:** запросы с точными кодами и с перефразировкой; документ, разорванный разбиением; отсутствие ответа в базе; конфликтующие версии документа; попытка инъекции через содержимое проиндексированного документа.

Источники: `references/source-book/chapter3.md:273`, `references/source-book/chapter3.md:425`, `references/source-book/chapter3.md:574`, `references/source-book/chapter3.md:630`.

## 14. Sessionless Resumable Worker

**Когда:** агент доступен постоянно, а сообщения пользователя разделены минутами или днями.

**Сигналы:** после паузы агент не помнит установленные зависимости и созданные файлы; продолжение задачи требует пересказа истории; перезапуск процесса теряет работу.

**Структура:** состояние задачи выносится за пределы процесса и делится на две части — перечень работ с отметками выполнения и рабочее окружение (файлы, зависимости). Роли разделяются: инициализатор декомпозирует задачу и создаёт перечень, исполнитель последовательно закрывает пункты.

**Инварианты:**

- каждый пункт перечня имеет признак завершённости; в книге его выставляет сам агент после прогона тестов, поэтому независимая проверка — усиление, которое стоит добавлять осознанно;
- шаг идемпотентен: повторное выполнение не создаёт дубль побочного эффекта;
- окружение либо сохраняется, либо воспроизводится из декларации;
- возобновление начинается с проверки фактического состояния, а не с доверия к записи.

**Стоимость:** декларативное описание окружения и дисциплина идемпотентности каждого шага.

**Проверка:** остановка процесса на каждом этапе с последующим возобновлением; расхождение записи и фактического состояния; повторная доставка одного и того же сообщения; параллельный запуск двух исполнителей на одном перечне.

Источники: `references/source-book/chapter5.md:82`, `references/source-book/chapter8.md:181`.

## 15. Post-Training Decision Gate

**Когда:** обсуждается дообучение модели под задачу.

**Сигналы:** «модель не понимает наш домен»; «давайте зафайнтюним» звучит раньше, чем построена оценка; проблема формулируется без указания failure mode.

**Порядок проверки — сверху вниз, остановка на первом сработавшем.** Если дошли до обучения, порядок внутри него обратный: сначала SFT стабилизирует формат вывода, затем RL. Пропуск SFT оправдан только для сильной базовой модели, уже выдающей нужный формат.

| Вопрос | Если да |
|---|---|
| Знание отсутствует в контексте? | контекст, Skill, база знаний |
| Модель неверно вызывает инструмент? | описание и схема инструмента |
| Нарушается ограничение? | политика и проверка в Harness |
| Нет способа измерить улучшение? | сначала eval-loop, дообучение бессмысленно |
| Нужен устойчивый формат вывода на распределении? | SFT |
| Среда развёртывания отличается от демонстраций? | RL |

**Инварианты:**

- базовая линия зафиксирована до обучения и измеряется тем же стендом;
- ограничения, нейтральные к результату, не выражаются через вознаграждение за результат — для них нужен отдельный проверяемый штраф;
- расхождения обучающей среды с целевой перечислены явно.

**Стоимость:** обучение требует данных, среды и цикла оценки; каждая из трёх составляющих дороже, чем правка Harness.

**Проверка:** сравнение с альтернативой на уровне Harness при равном бюджете; устойчивость на состояниях вне демонстраций; доля нарушений ограничений отдельно от доли успеха.

Источники: `references/source-book/chapter7.md:27`, `references/source-book/chapter7.md:305`, `references/source-book/chapter7.md:447`, `references/source-book/chapter7.md:581`, `references/source-book/chapter8.md:23`.

## 16. Untrusted Content Firewall

**Когда:** агент обрабатывает контент, который он не создавал: веб-страницы, письма, документы, результаты инструментов, записи собственной памяти.

**Сигналы:** агент выполнил инструкцию, найденную в документе; данные из внешнего источника попали в системный промпт; содержимое памяти влияет на политику.

**Структура:**

```text
внешний контент -> пометка provenance -> помещение в отведённую секцию
                -> инструкции внутри трактуются как данные
                -> enforcement вне prompt
```

**Инварианты:**

- недоверенный контент никогда не размещается там, где живут инструкции;
- разрешения не выводятся из содержимого контента;
- запись в долговременную память проходит ту же проверку доверия, что и внешний ввод, — иначе инструкция переживёт сессию;
- сомкнутая триада (доступ к приватным данным + недоверенный контент + внешний канал) требует разрыва хотя бы одного звена;
- контекстные меры — разметка источников, разделение инструкций и данных, очистка ввода — снижают вероятность атаки, но единственной защитой не служат: критические операции проверяет механизм за пределами контекста модели.

**Стоимость:** явная разметка источников на всех входах и запрет на «удобное» слияние контента с инструкциями.

**Проверка:** инъекция в читаемый документ, в результат инструмента и в записываемую память; попытка эскалации прав через содержимое; проверка, что триада разорвана; тест на сохранение вредоносной инструкции между сессиями.

Источники: `references/source-book/chapter2.md:655`, `references/source-book/chapter4.md:179`, `references/source-book/chapter5.md:92`, `references/source-book/chapter8.md:329`.
