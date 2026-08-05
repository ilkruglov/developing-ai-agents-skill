# Глава 4. Инструменты

## Основная идея

Инструмент — контролируемый интерфейс между решением модели и внешним миром. Его качество определяется не количеством функций, а ясностью выбора, точностью параметров, наблюдаемостью результата и enforceable safety boundary.

Источники: `references/source-book/chapter4.md:14`, `references/source-book/chapter4.md:41`.

## Классификация по назначению

- **Perception tools** получают новые наблюдения: search, read, vision, sensors.
- **Execution tools** изменяют внешнее состояние: write, send, deploy, transact.
- **Collaboration tools** передают task/state/artifacts другим исполнителям.
- **Event tools** запускают или прерывают работу по внешнему событию.

Risk policy следует из класса. Perception всё равно может утечь секрет или принести prompt injection; execution требует side-effect semantics; collaboration требует ownership и handoff schema; events требуют identity, deduplication и cancellation.

Источники: `references/source-book/chapter4.md:147`, `references/source-book/chapter4.md:179`, `references/source-book/chapter4.md:284`, `references/source-book/chapter4.md:347`.

## Tool или Skill + executor

Выбирай специализированный tool, если operation стабильна, параметры известны, а outcome должен быть строго проверен. Выбирай Skill + универсальный executor, если меняется стратегическая последовательность и требуется reasoning. Даже универсальный executor должен оставаться ограниченным permissions, sandbox и policy.

Источник: `references/source-book/chapter4.md:43`.

## Гранулярность

Слишком мелкие tools создают длинную хрупкую trajectory; слишком широкий tool скрывает решения, размывает permissions и усложняет verification. Объединяй действия, если они атомарны с точки зрения business transaction и rollback. Разделяй, если части имеют разные risk classes, approvals или independently useful observations.

Источники: `references/source-book/chapter4.md:58`, `references/source-book/chapter4.md:66`.

## Tool contract

Описание отвечает: когда применять, когда не применять, какие preconditions и какой результат. Schema закрывает неизвестные поля, различает optional/null, использует enum/ranges и не передаёт числа через двусмысленный текст. Result — discriminated union success/error с `call_id`, provenance, `retryable` и remediation.

Execution contract добавляет timeout, max output, idempotency key, transactional/partial-effect semantics, audit log и cancellation behavior. Проверка tool result происходит по внешнему state или детерминированному validator, а не по модели.

Источники: `references/source-book/chapter4.md:74`, `references/source-book/chapter4.md:90`, `references/source-book/chapter4.md:102`.

## MCP и большой каталог tools

Протокол подключения tools не решает selection и security. Большой каталог увеличивает prompt footprint и ошибки выбора. Используй capability discovery/progressive disclosure: сначала metadata, затем schema выбранного tool. Фиксируй server identity/version и применяй allowlist/permissions к каждому capability.

Источник: `references/source-book/chapter4.md:110`.

## Event-driven agent

Для долгоживущей системы событие — envelope с `event_id`, source identity, timestamp, type, payload schema и dedupe key. Dispatcher проверяет policy и создаёт versioned run. Синхронную генерацию нельзя просто «магически прервать»: controller должен управлять cancellation token, tool lifecycle и публикацией устаревших результатов.

Источники: `references/source-book/chapter4.md:347`, `references/source-book/chapter4.md:387`, `references/source-book/chapter4.md:399`, `references/source-book/chapter4.md:415`, `references/source-book/chapter4.md:429`, `references/source-book/chapter4.md:504`.

## Антипаттерны

- `execute(command: string)` с полными правами как единственный tool.
- Tool description, перечисляющее возможности, но не routing conditions.
- Retry write без idempotency.
- Вывод stack trace/секрета в prompt.
- «Успех» без прочтения внешнего состояния.
- MCP server, автоматически получающий все credentials.
- Event replay, создающий дублирующий side effect.

## Eval

Тестируй valid/invalid schema, ambiguous selection, parameter boundary, timeout, retry, duplicate call, partial success, permission denial, prompt injection, output truncation и cancellation. Метрики: selection accuracy, argument validity, external outcome, unsafe attempt/allow rate, repeat-call rate и recovery success.
