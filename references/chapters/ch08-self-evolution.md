# Глава 8. Самоэволюция AI-агента

## Основная идея

Агент не учится автоматически от факта выполнения задач. Без явного механизма следующая сессия не получает предыдущий опыт, а сырые логи не становятся надёжным знанием. Безопасная самоэволюция — externalized learning: опыт превращается в проверяемые, версионируемые memory/knowledge/Skills/tools без изменения весов.

Источники: `references/source-book/chapter8.md:11`, `references/source-book/chapter8.md:23`, `references/source-book/chapter8.md:49`.

## Три парадигмы

1. **Post-training:** устойчиво меняет веса; дорогой отдельный pipeline.
2. **In-context learning:** временно адаптирует модель внутри текущего context.
3. **Externalized learning:** сохраняет изменения в прозрачном внешнем carrier.

Для v1 с frozen model третий путь даёт auditability, исправление и rollback. Он не гарантирует улучшение: promotion должен пройти eval.

Источник: `references/source-book/chapter8.md:23`.

## Experience pipeline

Immutable episode содержит task, environment version, trajectory, tool evidence, external outcome и failure labels. Extraction создаёт candidate, а не правило. Candidate объединяет повторяемую стратегию, preconditions, failure boundary, supporting/contradicting episodes и confidence.

Учись и на успехе, и на неудаче. Неудача полезна после причинной классификации: missing knowledge, wrong tool selection, bad arguments, broken environment, insufficient constraint, poor planning или random/transient failure. Иначе система закрепит случайную корреляцию.

Источники: `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`.

## Skills и instruction optimization

Skill хранит меняющийся предметный workflow и загружается по необходимости. Версионируй description/routing, procedure, examples и references. Изменение system instructions проходит как code change: diff, source episodes, dev eval, locked holdout, security review, canary и rollback.

«Sleep consolidation» может асинхронно дедуплицировать и организовывать memory, но не должно бесконтрольно повышать candidates в production. Cross-session continuation использует durable state, а не скрытое «воспоминание» модели.

Источники: `references/source-book/chapter8.md:113`, `references/source-book/chapter8.md:127`, `references/source-book/chapter8.md:145`, `references/source-book/chapter8.md:181`.

## Tool discovery и creation

Безопасный lifecycle:

```text
need detected
 -> search approved registry
 -> inspect identity/version/provenance
 -> static policy/dependency review
 -> sandboxed contract + adversarial tests
 -> permission/egress/secret review
 -> human approval for risky capability
 -> shadow/canary
 -> signed/versioned promotion
```

Если подходящего tool нет, агент может предложить код. Generated tool остаётся недоверенным. Он не получает credentials/network/host filesystem до отдельного approval. Храни source, build inputs, dependencies, tests и owner.

Источники: `references/source-book/chapter8.md:187`, `references/source-book/chapter8.md:191`, `references/source-book/chapter8.md:224`, `references/source-book/chapter8.md:236`, `references/source-book/chapter8.md:246`, `references/source-book/chapter8.md:258`, `references/source-book/chapter8.md:273`.

## Носители накопления

- facts → knowledge base;
- scoped user facts/preferences → typed memory;
- repeatable parameterized operations → code/tool;
- changing strategic processes → Skill;
- broad policy behavior → отдельно обоснованный post-training.

Связывай derived artifact с origin. Rollback кандидата должен отключать зависимые instruction/tool versions. Удаление исходных пользовательских данных должно распространяться на производные записи по policy.

Источник: `references/source-book/chapter8.md:319`.

## Safety boundaries

- trusted и untrusted experience разделены;
- content из web/tool/log не интерпретируется как policy;
- promotion требует независимого evidence;
- capability escalation запрещён по умолчанию;
- memory poisoning и correlated episodes тестируются;
- release gate включает regression и safety, не только средний success;
- у каждой версии есть kill switch/rollback.

Источник: `references/source-book/chapter8.md:329`.

## Антипаттерны

- Append raw successful response в system prompt.
- Делать глобальное правило из одного failure.
- Самостоятельно скачивать и запускать tool с сетью/секретами.
- Оптимизировать prompt на тех же задачах, которыми измеряется improvement.
- Считать рост количества memories ростом мастерства.
- Rollback instruction, оставляя созданный ею tool активным.

## Eval

Используй chronological split: агент видит train episodes, но не future holdout. Сравни frozen baseline и accumulating variant на одинаковых budgets. Добавь poisoned/contradictory episodes, changed environment, deletion и rollback. Метрики: holdout outcome over time, regression, unsafe promotion, stale-memory application, provenance coverage и recovery after rollback.
