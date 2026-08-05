# Глава 10. Совместная работа нескольких AI-агентов

## Основная идея

Multi-agent — способ разделить контекст, работу и контроль, а не автоматический усилитель интеллекта. Его польза появляется, когда взаимодействие приносит новое внешнее evidence, обеспечивает независимую проверку или параллелит действительно независимые задачи. Обсуждение одной и той же информации может лишь умножить стоимость и ошибку.

Источник: `references/source-book/chapter10.md:65`.

## Две оси классификации

### Контекст

- **Shared context:** роли сменяются внутри общей trajectory; handoff дешёвый, но ошибки/шум общие.
- **Isolated contexts:** каждый агент получает bounded contract; лучше separation и parallelism, но нужен явный artifact handoff.

### Топология

- **Peer:** участники взаимно проверяют/улучшают.
- **Manager:** координатор декомпозирует, назначает и интегрирует.
- **Decentralized:** управление передаётся между peers по protocol.

Зафиксируй обе оси до реализации: слово «multi-agent» не описывает архитектуру.

Источники: `references/source-book/chapter10.md:11`, `references/source-book/chapter10.md:15`, `references/source-book/chapter10.md:53`, `references/source-book/chapter10.md:94`, `references/source-book/chapter10.md:196`, `references/source-book/chapter10.md:251`, `references/source-book/chapter10.md:287`, `references/source-book/chapter10.md:431`.

## Criterion: new information

Назови конкретный новый signal каждой роли: результат теста, поиск в независимом источнике, runtime trace, render, user feedback, measurement или domain-specific computation. Если роли только переформулируют одну input history, сначала сравни с single-agent self-check/best-of-N.

Verifier должен читать первичный artifact/evidence. Если он видит только confident summary proposer-а, ошибки коррелированы.

Источник: `references/source-book/chapter10.md:65`.

## Data plane и control plane

**Data plane:** files, artifacts, test results, versions, ownership, provenance. Shared filesystem удобна как общий мир, но требует worktrees/locks/ownership и atomic handoff.

**Control plane:** task IDs, messages, dependency graph, status/heartbeat, budgets, cancellation, retry и escalation. Не используй случайный текстовый чат как единственный task state.

Источники: `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`.

## Manager pattern

Manager передаёт worker-у:

```yaml
objective: one bounded outcome
scope: owned files/resources
inputs: immutable evidence pointers
constraints: explicit
budget: steps/tokens/time/tools
deliverable: structured artifact schema
acceptance: executable checks
```

Worker не должен принимать product-wide решения вне scope. Manager интегрирует artifacts, разрешает dependencies и запускает cross-cutting verification. Heartbeat показывает progress/blocker, но не заменяет deliverable.

## Failure modes

### Shared filesystem conflict

Два агента изменяют один файл/состояние на основе разных версий. Используй exclusive ownership, separate worktrees, compare-and-swap или optimistic locking. Проверяй stale write перед merge.

### Cascading error

Первый ошибочный claim превращается в premise следующих ролей. Передавай provenance/evidence, отмечай uncertainty, используй independent verifier и circuit breaker. Manager не должен «усреднять» несовместимые факты.

### Coordination overhead

Декомпозиция, сериализация context, ожидание и synthesis могут стоить больше работы. Мерь wall time, tokens, tool calls и integration failures.

Источники: `references/source-book/chapter10.md:481`, `references/source-book/chapter10.md:493`, `references/source-book/chapter10.md:511`.

## Антипаттерны

- Фиксированные пять агентов для каждого запроса.
- Роли с разными названиями, но одинаковым context/tools.
- Несколько writers одного файла без ownership.
- Verifier, читающий только reasoning proposer-а.
- Manager, повторно решающий все подзадачи вместо проверки artifacts.
- Retry failed worker без изменения condition.

## Equal-budget eval

Сравни:

1. single-agent baseline;
2. single-agent с тем же дополнительным token/tool budget;
3. adaptive multi-agent routing;
4. always-multi-agent как контроль.

Используй одинаковые tasks/environment и external oracle. Мерь outcome, latency, cost, handoff/integration error, correlated false accept и cascade depth. Multi-agent проходит gate, только если улучшает целевой trade-off, а не только один judge score.

Каскадный тест должен быть отдельным: внедри одинаковое правдоподобное ошибочное upstream evidence или conclusion, затем измерь долю downstream-ролей, принявших ошибку, глубину распространения и итоговый external harm. Обычная метрика handoff/schema errors этого не показывает.
