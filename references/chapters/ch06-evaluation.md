# Глава 6. Оценка AI-агента

## Основная идея

Оценка — не финальный отчёт, а инфраструктура разработки. Она превращает vague improvement в falsifiable hypothesis и связывает traces с конкретным изменением Harness/model/data. Без воспроизводимой среды и набора задач сравнение агентов не имеет надёжного смысла.

Источники: `references/source-book/chapter6.md:29`, `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:563`.

## Evaluation environment

Среда задаёт initial state, доступные tools, user/environment responses, budgets и terminal outcome. Пинь версии model, prompt, tool schemas, corpus/data, simulator и dependencies. Сохраняй trajectory и external state, чтобы результат можно было воспроизвести.

Human-in-the-loop сценарии требуют simulators или recorded interactions, но обязательно измеряй разрыв симуляции и production. Domain randomization помогает не переобучиться на один хрупкий simulator.

Источники: `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:91`, `references/source-book/chapter6.md:110`, `references/source-book/chapter6.md:679`, `references/source-book/chapter6.md:699`.

## Dataset design

Task description содержит initial conditions, allowed actions, expected outcome и objective verification. Стратифицируй difficulty и реальное распределение; включай edge/adversarial cases. Отделяй development от locked holdout. Дедуплицируй и контролируй leakage из training/prompts.

Источники: `references/source-book/chapter6.md:157`, `references/source-book/chapter6.md:167`, `references/source-book/chapter6.md:179`, `references/source-book/chapter6.md:197`, `references/source-book/chapter6.md:205`, `references/source-book/chapter6.md:223`.

## Metrics stack

Не своди качество к одному score:

- **Outcome:** task success, correctness, completion.
- **Safety/constraints:** нарушения и unsafe attempts.
- **Trajectory:** invalid/repeated calls, unnecessary steps, recovery.
- **Experience:** latency, interruption, clarity, user effort.
- **Resources:** tokens, model/tool cost, wall time.
- **Reliability:** variance, tail failures, forced-restart success.

Гейт может требовать non-inferiority по safety/cost и improvement по primary outcome.

Источник: `references/source-book/chapter6.md:239`.

## Automated grading

Предпочитай deterministic oracle, schema/test или external state. LLM-as-a-Judge применяй для open-ended qualities по точной rubric. Используй blinded ordering, pairwise comparison, multiple judges при необходимости и human calibration. Проверяй position, verbosity и self-preference bias; judge disagreement — сигнал uncertainty.

Источники: `references/source-book/chapter6.md:278`, `references/source-book/chapter6.md:284`, `references/source-book/chapter6.md:401`.

## Статистика и честное сравнение

Стохастический агент требует повторных прогонов. Сообщай sample size, central estimate, confidence interval и paired delta. Equal-budget comparison фиксирует tokens, tool calls, wall time или cost; если архитектуры используют разные ресурсы, показывай Pareto frontier вместо скрытия разницы.

Источник: `references/source-book/chapter6.md:421`, `references/source-book/chapter6.md:444`, `references/source-book/chapter6.md:520`.

## Observability → hypothesis → ablation

Trace связывает decision, context version, tool call/result, verifier и state transition. Кластеризуй failures; сформулируй одну причинную гипотезу; измени один механизм; проведи ablation. Feature flags должны позволять выключить новую функцию и отделить mechanism от goal.

Источники: `references/source-book/chapter6.md:494`, `references/source-book/chapter6.md:534`, `references/source-book/chapter6.md:573`, `references/source-book/chapter6.md:585`, `references/source-book/chapter6.md:595`, `references/source-book/chapter6.md:609`, `references/source-book/chapter6.md:635`, `references/source-book/chapter6.md:641`, `references/source-book/chapter6.md:653`.

## Антипаттерны

- Оценивать на тех же примерах, по которым правили prompt.
- Использовать agent self-report как success oracle.
- Сравнивать five-agent с single-agent при 5× budget и объявлять архитектурную победу.
- Показывать среднее без tails/variance.
- Менять model, prompt и tools одновременно.
- Выпускать «улучшение» без rollback и production drift metrics.

## Eval specification template

```yaml
hypothesis: falsifiable statement
baseline: pinned bundle
variant: one controlled delta
tasks: dev + locked_holdout + adversarial
budgets: token/tool/time/cost
primary_metric: external outcome
guardrails: safety + cost + latency
repetitions: justified N
statistics: paired delta + interval
release_gate: preregistered
rollback: verified
```
