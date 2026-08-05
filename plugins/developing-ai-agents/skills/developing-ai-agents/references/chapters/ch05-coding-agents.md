# Глава 5. Coding Agent и генерация кода

## Основная идея

Coding Agent силён не только генерацией текста: код становится метаспособностью для вычисления, проверки, адаптации систем и создания новых tools. Поэтому production Coding Agent требует особенно строгого Harness: repo awareness, безопасное исполнение, точное редактирование, тесты, recovery и durable state.

Источники: `references/source-book/chapter5.md:15`, `references/source-book/chapter5.md:354`.

## Минимальный цикл

```text
understand task
 -> inspect repository/instructions
 -> establish baseline
 -> plan bounded change
 -> add failing test
 -> edit narrow scope
 -> run focused verification
 -> inspect diff
 -> broader verification
 -> report evidence/remaining risk
```

LLM не является source of truth для symbols/types/references: используй compiler, LSP, test runner и runtime traces. Search и edit tools должны сохранять точные file/line anchors, diff и artifact provenance.

Источники: `references/source-book/chapter5.md:146`, `references/source-book/chapter5.md:188`, `references/source-book/chapter5.md:311`, `references/source-book/chapter5.md:335`.

## Sessionless и durable work

Long task не должен зависеть от одной chat session. Храни goal, constraints, decisions, patch state, test evidence и next action вне transcript. Новый episode восстанавливается из repo state и typed checkpoint; он перепроверяет изменчивые предположения.

Источник: `references/source-book/chapter5.md:82`.

## Safety model

- sandbox untrusted builds/tests;
- scope filesystem и network;
- не раскрывай secrets процессу по умолчанию;
- read-only diagnosis не превращай в edit;
- destructive/irreversible operation требует explicit approval;
- inspect exact target перед mutation;
- сохраняй rollback path и diff.

Prompt policy помогает выбору, но enforcement должен находиться в executor/permissions.

Источник: `references/source-book/chapter5.md:92`.

## Recovery

Ошибка компиляции или теста — observation, а не повод многократно повторять ту же команду. Классифицируй failure: environment, dependency, syntax/type, behavioral assertion, flaky/external, permission или resource. Обновляй state и гипотезу. Retry допустим только при изменившемся condition или известном transient error.

Checkpoint сохраняет exact command, exit status, relevant output, changed files и next diagnostic. Если исправление расширяет scope, остановись и переоцени plan.

Источник: `references/source-book/chapter5.md:233`.

## Code as meta-capability

Код полезен как:

- точное вычисление вместо словесного рассуждения;
- executable business constraint;
- adapter между несовместимыми системами;
- генератор/преобразователь media;
- UI, создаваемый под конкретную задачу;
- новый tool, проходящий безопасный lifecycle.

Но сгенерированный код не становится доверенным из-за того, что его написал агент. Требуются provenance, review, tests, sandbox и promotion gate.

Источники: `references/source-book/chapter5.md:373`, `references/source-book/chapter5.md:415`, `references/source-book/chapter5.md:509`, `references/source-book/chapter5.md:573`, `references/source-book/chapter5.md:614`, `references/source-book/chapter5.md:693`.

## Антипаттерны

- Редактировать до чтения repo instructions и baseline.
- Делать broad rewrite при локальном bug.
- Заявлять «тесты прошли», не приводя command/output.
- Использовать transcript как единственный checkpoint.
- Игнорировать dirty worktree и перетирать чужие изменения.
- Запускать произвольный generated code с host credentials/network.
- Подменять LSP/компилятор предположением о symbol usage.

## Eval

Используй репозитории-задачи с deterministic tests, hidden tests, dirty-worktree cases, forced restart, misleading failure, dependency/network denial и malicious file content. Измеряй task success, regression, diff scope, unsafe action attempts, number of failed loops, recovery и reproducibility.
