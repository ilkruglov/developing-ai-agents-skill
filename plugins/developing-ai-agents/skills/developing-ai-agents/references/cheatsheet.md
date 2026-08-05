# Шпаргалка по разработке AI-агентов

Быстрые таблицы для решения на месте. Если задача требует процедуры, а не одного решения, переходи к playbook:

| Задача | Процедура |
|---|---|
| Спроектировать агента | `references/playbooks/design-agent.md` |
| Разобрать trace | `references/playbooks/diagnose-trace.md` |
| Провести review | `references/playbooks/harness-review.md` |
| Построить evals | `references/playbooks/build-evals.md` |
| Спроектировать память | `references/playbooks/memory-design.md` |
| Задать бюджет задержки | `references/playbooks/realtime-latency.md` |
| Выбрать между одним агентом и несколькими | `references/playbooks/multi-agent-choice.md` |

## 1. Нужен ли агент

| Ситуация | Минимальный механизм |
|---|---|
| Один предсказуемый ответ, нет действий | один вызов LLM |
| Последовательность известна заранее | deterministic workflow |
| Следующий шаг зависит от результата tool/environment | один агент с bounded ReAct loop |
| Независимые задачи можно параллелить | изолированные workers + manager |
| Роль получает новое внешнее evidence и проверяет другую роль | proposer/verifier или specialist agents |
| Пять ролей обсуждают тот же текст без новых данных | оставить одного агента; измерить best-of-N отдельно |

Красные флаги преждевременной автономности: нет terminal conditions, tool side effects не ограничены, задача непроверяема, нет event log, нет baseline.

Источник: `references/source-book/chapter1.md:295-386`, `references/source-book/chapter10.md:65-93`.

## 2. Карта диагностики

| Симптом | Сначала проверить | Не считать доказанным без |
|---|---|---|
| Агент забывает ограничения | context projection, explicit state, compression | trace до и после потери ограничения |
| Повторяет tool calls | structured errors, idempotency, progress state, loop detector | event sequence с одинаковыми входами/результатами |
| Галлюцинирует результат действия | tool result provenance, verifier | сверка с внешним состоянием |
| Хорош на демо, плох в production | dataset distribution, judge calibration, drift | representative holdout и production telemetry |
| Дорогой и медленный | steps, tool latency, prompt prefix/cache, retries | stage-level p50/p95 и token/tool budget |
| Multi-agent ухудшает ответ | evidence independence, topology, handoff loss | equal-budget A/B и cascade-error trace |
| «Самообучение» деградирует | promotion pipeline, poisoning, stale memory | versioned benchmark и rollback test |

Расширенный каталог симптомов с причинами и заменами: `references/antipatterns.md`. Пошаговый разбор: `references/playbooks/diagnose-trace.md`.

## 3. Минимальный Harness v1

```text
request
  -> policy/permission gate
  -> context builder(static prefix + state + bounded trajectory)
  -> LLM decision(schema)
  -> tool gateway(timeout + idempotency + sandbox)
  -> external observation
  -> verifier
  -> state transition/checkpoint
  -> continue | recover | escalate | finish
```

Обязательные поля run:

```yaml
run_id: stable-id
goal: exact outcome
state_version: monotonic
constraints: []
completed: []
active_step: string
artifacts: []
budgets:
  max_steps: integer
  deadline: timestamp
  max_tokens: integer
  max_cost: number
cancellation_token: id
terminal_state: running|succeeded|failed|cancelled|blocked
```

## 4. Tool contract

```yaml
name: stable_verb_noun
purpose: one capability
input_schema: closed typed object
output_schema: success or structured error
preconditions: []
side_effects: none|reversible|irreversible
permissions: [read:path]
timeout_ms: integer
retry:
  safe: boolean
  max_attempts: integer
idempotency_key: required_if_side_effect
provenance:
  call_id: required
  source_version: required
approval: required_for_high_risk
```

Не отдавай агенту секреты «на всякий случай». Не смешивай read и destructive write в одном широком tool. Возвращай причину, `retryable` и remediation вместо неструктурированного stack trace.

Источник: `references/source-book/chapter4.md:14-109`, `references/source-book/chapter1.md:387-422`.

## 5. Context lifecycle

```text
static prefix
  system policy + stable tool schemas

dynamic projection
  current goal + constraints + status + relevant memory
  + bounded recent trajectory + selected evidence
```

Порядок борьбы с раздуванием:

1. Ограничь/вынеси полный tool output в артефакт.
2. Удали шум и дубли.
3. Сверни повторяющиеся структуры.
4. Архивируй завершённый этап в typed summary.
5. Пересобери контекст из durable state как circuit breaker.
6. Отдай независимую подзадачу в изолированный контекст.

Никогда не теряй при rollover: цель, decisions, constraints, artifact IDs, file changes, test evidence, open risks, next action, rollback.

Источник: `references/source-book/chapter2.md:355-559`, `references/source-book/chapter2.md:763-1061`.

## 6. Память и обучение

| Содержание | Носитель | Gate |
|---|---|---|
| пользовательский факт | typed memory | consent, provenance, retention |
| предметный факт | knowledge base | source, freshness, conflict policy |
| повторяемая операция | code/tool | tests, sandbox, permissions |
| стратегия/workflow | Skill | multi-episode evidence, eval, review |
| изменение поведения модели | post-training | отдельный data/training/safety pipeline |

Promotion:

```text
raw episode
  -> redact + classify
  -> extract candidate
  -> deduplicate/conflict check
  -> offline eval on dev + holdout
  -> human/policy approval
  -> canary
  -> promote or rollback
```

Источник: `references/source-book/chapter3.md:17-272`, `references/source-book/chapter8.md:23-180`, `references/source-book/chapter8.md:319-355`.

## 7. Eval card

```yaml
hypothesis: one falsifiable mechanism
baseline: pinned versions
variant: one controlled change
dataset:
  dev: representative cases
  holdout: unseen locked cases
  adversarial: abuse and failure cases
budgets:
  tokens: equal
  tools: equal
  wall_time: equal_or_reported
metrics:
  outcome: external success
  safety: violations
  trajectory: invalid/repeated calls
  efficiency: latency/tokens/cost/steps
  recovery: forced-failure success
statistics: repeated runs + confidence interval
release_gate: preregistered threshold
rollback: tested version switch
```

Для LLM-as-a-Judge: слепой порядок вариантов, точная rubric, калибровка на размеченной человеком выборке, проверка position/verbosity bias.

Источник: `references/source-book/chapter6.md:71-238`, `references/source-book/chapter6.md:239-533`, `references/source-book/chapter6.md:631-678`.

## 8. Realtime voice

| Архитектура | Сильная сторона | Основной риск | Хорошая роль |
|---|---|---|---|
| Cascading | контроль, сменяемость компонентов, observability | накопление задержки и потери между ASR/LLM/TTS | production v1 |
| Omni | меньше промежуточных представлений | слабее контроль и диагностика | исследовательская/поддерживаемая провайдером ветка |
| Full-Duplex | естественный barge-in и параллельное восприятие | гонки, cancellation, сложная safety | после зрелого streaming Harness |

Fast path отвечает, подтверждает и поддерживает turn-taking. Slow path получает versioned snapshot и возвращает structured result. Перед публикацией сверяй `turn_id/state_version`; при barge-in отменяй TTS, generation и side-effecting work по отдельным правилам.

Источник: `references/source-book/chapter9.md:28-287`.

## 9. Multi-agent

Перед запуском запиши:

- axis 1: `shared_context | isolated_contexts`;
- axis 2: `peer | manager | decentralized`;
- что именно является новым evidence каждой роли;
- ownership файлов/ресурсов;
- handoff schema и acceptance criteria;
- cancellation/timeout/heartbeat;
- кто проверяет результат и читает ли он первичные источники.

Data plane: versioned artifacts/files. Control plane: задачи, сообщения, статусы, отмена. При общей FS нужны ownership, worktree или optimistic lock. Проверяй конфликт записи и каскадное усиление ошибки.

Источник: `references/source-book/chapter10.md:11-64`, `references/source-book/chapter10.md:196-533`.
