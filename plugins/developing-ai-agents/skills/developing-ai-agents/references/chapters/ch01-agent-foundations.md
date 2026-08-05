# Глава 1. Введение в AI-агентов

## Основная идея

Минимальная модель системы: **AI-агент = LLM + контекст + инструменты**. LLM выбирает действие, context поставляет наблюдаемую картину задачи, tools воздействуют на среду. Цикл ReAct делает это последовательным, а Harness превращает цикл в production-систему.

Источники: `references/source-book/chapter1.md:13`, `references/source-book/chapter1.md:43`, `references/source-book/chapter1.md:88`, `references/source-book/chapter1.md:122`, `references/source-book/chapter1.md:146`.

## Framework: пять функций Harness

1. **Context:** обеспечить информационную достаточность следующего шага.
2. **Tools:** предоставить ясный Agent–Computer Interface.
3. **Constraints:** задать безопасные defaults и границы возможностей.
4. **Verification:** проверить outcome по структурированному независимому входу.
5. **Correction:** обнаружить ошибку, восстановиться или честно эскалировать.

Это не пять независимых checkbox. Tool result должен стать observation, verifier — обновить state, correction — выбрать ограниченный следующий переход. Иначе цикл разомкнут.

Источники: `references/source-book/chapter1.md:230`, `references/source-book/chapter1.md:272`, `references/source-book/chapter1.md:280`.

## Decision rules

- Если шаги известны заранее, используй workflow.
- Если следующий шаг зависит от нового наблюдения, добавляй bounded autonomy.
- Если задачу можно решить без side effects, не выдавай write capability.
- Если outcome нельзя проверить, сначала спроектируй environment/oracle.
- Если отказ инструмента не меняет state, следующий model turn почти наверняка повторит действие.
- Сначала улучшай ACI и Harness; смену модели проверяй как отдельную гипотезу.

Источники: `references/source-book/chapter1.md:295`, `references/source-book/chapter1.md:307`, `references/source-book/chapter1.md:324`, `references/source-book/chapter1.md:387`.

## Техника: architecture trace

Для одного реального run составь таблицу:

| Шаг | Context evidence | Model decision | Tool contract | External result | Verification | State change |
|---|---|---|---|---|---|---|

Пустая колонка показывает разрыв. Например, tool вернул неструктурированную строку, verifier отсутствует, state не отмечает выполненное действие — повтор на следующем шаге ожидаем даже при сильной модели.

## Антипаттерны

- «Агент» как бесконечный while-loop вокруг LLM.
- Огромный system prompt вместо enforcement в коде.
- Считать сообщение модели «готово» подтверждением внешнего результата.
- Давать модели десятки перекрывающихся tools без ясного выбора.
- Строить multi-agent до работающего single-agent baseline.
- Скрывать permanent failure за неограниченными retries.

## Рабочий пример

Задача: агент обрабатывает возврат товара.

Минимальная архитектура: workflow собирает order ID и причину; агент используется только для понимания запроса и выбора разрешённого пути. Read tool получает заказ. Policy проверяет срок и права. Write tool имеет idempotency key и approval для нестандартной суммы. Verifier повторно читает состояние заказа. Correction разрешает один retry для timeout, но не для policy denial. Так формула реализована в runtime, а не остаётся метафорой.

## Проверка усвоения

Для любого предлагаемого компонента ответь:

- какую из трёх частей формулы он улучшает;
- какую функцию Harness реализует;
- какое внешнее наблюдение доказывает его работу;
- что произойдёт при timeout, неверном output и отмене.

Если ответов нет, компонент пока является идеей, а не архитектурой.
