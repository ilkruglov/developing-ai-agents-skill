# Паттерны проектирования AI-агентов

Каждый паттерн связывает failure mode, механизм и способ проверки. Не применяй паттерн без наблюдаемой проблемы или требования.

## 1. Bounded ReAct Harness

**Когда:** следующий шаг зависит от результата внешнего действия.

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

**Проверка:** scripted environment с успешной траекторией, retryable error, permanent error, repeated action, timeout, cancellation и ложным заявлением модели об успехе.

Источники: `references/source-book/chapter1.md:146`, `references/source-book/chapter1.md:230`, `references/source-book/chapter2.md:86`.

## 2. Stable Prefix + Dynamic Projection

**Когда:** длинные сессии дороги, теряют constraints или плохо используют prompt cache.

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

**Проверка:** prefix hash/cache-hit telemetry, token composition по секциям, forced rollover и восстановление всех constraints после нескольких циклов сжатия.

Источники: `references/source-book/chapter2.md:355`, `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:887`.

## 3. Durable State, Ephemeral Episodes

**Когда:** Coding Agent работает долго, должен переживать restart или продолжать задачу между сессиями.

**Структура:** durable state хранит цель, decisions, constraints, progress, artifacts, test evidence, pending risks и next action. Новый episode получает компактную проекцию и последние релевантные events.

**Правило:** transcript — доказательный журнал, но не единственный source of truth. Обновление состояния имеет version/compare-and-swap или transactional boundary.

**Проверка:** принудительно остановить run на нескольких этапах; восстановить его в новом процессе; сравнить итог и соблюдение constraints с непрерывным baseline.

Источники: `references/source-book/chapter2.md:763-935`, `references/source-book/chapter5.md:82`, `references/source-book/chapter5.md:233`, `references/source-book/chapter8.md:181`.

## 4. Progressive Context Reduction

**Когда:** контекст раздувается или retrieval ухудшается задолго до жёсткого token limit.

**Уровни:**

1. full tool output → external artifact + bounded excerpt;
2. noise/duplicate deletion;
3. micro-compression повторяющихся result structures;
4. typed archival summary завершённой фазы;
5. full reconstruction из durable state как circuit breaker.

Независимую задачу лучше вынести в child context, чем сжимать всё для одного гигантского контекста.

**Проверка:** gold facts/constraints seeded в ранних шагах; после каждого уровня агент должен воспроизвести и применить их. Измеряй не только tokens, но task success, cache reuse и repeated actions.

Источники: `references/source-book/chapter2.md:936-1061`.

## 5. Capability-Gated Tool Gateway

**Когда:** агент читает/изменяет внешние системы, запускает код или использует сеть.

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

**Проверка:** prompt injection, path/scope escape, secret exfiltration, network egress, duplicate request, timeout, partial side effect, forged tool result.

Источники: `references/source-book/chapter1.md:387`, `references/source-book/chapter4.md:41`, `references/source-book/chapter4.md:179`, `references/source-book/chapter4.md:415`, `references/source-book/chapter8.md:329`.

## 6. Tool/Skill/Knowledge Carrier Selection

**Когда:** появляется новая повторяемая capability.

| Нужда | Носитель |
|---|---|
| Найти подтверждённый факт | knowledge base/RAG |
| Выполнить стабильную параметризуемую операцию | code/tool |
| Следовать меняющейся стратегии с reasoning | Skill |
| Запомнить состояние конкретного пользователя | typed user memory |
| Изменить базовое поведение на распределении задач | post-training |

**Антипаттерны:** помещать бизнес-правило только в prompt, сохранять скрипт как неструктурированный memory item, превращать единичный log в глобальный Skill.

**Проверка:** carrier должен иметь schema/version/provenance, isolated test и lifecycle удаления/rollback.

Источники: `references/source-book/chapter3.md:94`, `references/source-book/chapter4.md:43`, `references/source-book/chapter8.md:113`, `references/source-book/chapter8.md:319`.

## 7. Evidence-Gated Self-Improvement

**Когда:** агент должен учиться на выполненных задачах без постоянного fine-tuning.

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

**Проверка:** hidden holdout, temporal split, poisoned episodes, conflicting experiences, stale tool version, deletion request и transitive rollback всех derived artifacts.

Источники: `references/source-book/chapter8.md:23`, `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`, `references/source-book/chapter8.md:127`, `references/source-book/chapter8.md:145`, `references/source-book/chapter8.md:319`, `references/source-book/chapter8.md:329`.

## 8. Evaluation Flywheel

**Когда:** до первой оптимизации и после каждого изменения агента.

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

**Проверка:** reproduce baseline; force one known failure; ensure metric detects it; test rollback before release.

Источники: `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:157`, `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:563`, `references/source-book/chapter6.md:635`.

## 9. Proposer–Verifier with Independent Evidence

**Когда:** результат важен, а deterministic oracle неполон; второй исполнитель может независимо проверить первичные данные.

Proposer отдаёт claim + artifact + evidence pointers. Verifier получает task contract и первичные artifacts, но не chain-of-thought и не авторитетный «правильный ответ» proposer-а. Verifier должен иметь возможность вернуть `pass`, `fail` или `unknown` с evidence.

**Не применять:** обе роли видят один текст, не используют tools/evidence и лишь голосуют. Это self-consistency/best-of-N, а не независимая проверка.

**Проверка:** inject plausible wrong proposal; verifier обязан обнаружить его по source/test. Измерь correlated error rate и false accept.

Источники: `references/source-book/chapter6.md:278-420`, `references/source-book/chapter10.md:65`, `references/source-book/chapter10.md:251`.

## 10. Manager + Isolated Workers

**Когда:** задача распадается на независимые bounded subtasks и выигрывает от параллельной работы.

Manager создаёт contract: objective, allowed scope, inputs, expected artifact schema, budget и acceptance test. Worker получает минимальный context и владеет отдельным artifact/worktree. Manager объединяет результаты по schema и запускает общую интеграционную проверку.

**Failure controls:** lease/heartbeat, timeout, cancellation, no overlapping ownership, immutable handoff, merge conflict policy, bounded retry и circuit breaker при повторяющемся blocker.

**Проверка:** lost worker, duplicate completion, stale handoff, conflicting writes, wrong manager synthesis и cascading error.

Источники: `references/source-book/chapter2.md:1054`, `references/source-book/chapter10.md:196`, `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`, `references/source-book/chapter10.md:287`, `references/source-book/chapter10.md:481`.

## 11. Fast/Slow Realtime Loop

**Когда:** интерфейс должен реагировать быстрее, чем выполняется полное рассуждение.

Fast path отвечает за turn-taking, acknowledgement, короткие безопасные ответы и barge-in. Slow path работает с versioned snapshot, выполняет reasoning/tools и возвращает structured result. Dispatcher публикует результат только если `turn_id` и `state_version` актуальны.

Cancellation разделяй:

- остановить generation;
- остановить TTS/вывод;
- отменить tool, если он cancellable;
- не повторять необратимый side effect;
- компенсировать уже выполненный reversible side effect.

**Проверка:** partial ASR correction, пользователь перебил до/после tool call, slow result пришёл после нового turn, TTS уже начал воспроизведение, сеть потеряна в середине stream.

Источники: `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:94`, `references/source-book/chapter9.md:174`, `references/source-book/chapter9.md:192`, `references/source-book/chapter9.md:276`.

## 12. Source-Grounded Recommendation

**Когда:** решение должно быть проверяемо и связано с книгой.

Для каждого важного вывода укажи:

1. project evidence — код/trace/metric;
2. применённый принцип — точный `references/source-book/*.md:line`;
3. inference — почему принцип подходит к этому failure mode;
4. falsification test — что могло бы опровергнуть решение.

Книжная ссылка не подтверждает текущий provider fact. Для моделей/API/цен используй актуальную первичную документацию и дату проверки.
