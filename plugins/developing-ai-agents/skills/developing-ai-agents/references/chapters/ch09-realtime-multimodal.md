# Глава 9. Мультимодальность и взаимодействие в реальном времени

## Основная идея

Realtime agent проектируется вокруг latency, concurrency, interruption и state consistency, а не только вокруг качества финального ответа. Голос и GUI/robot control создают непрерывный поток наблюдений, где устаревшее решение может стать вредным ещё до завершения model turn.

Источник: `references/source-book/chapter9.md:20`.

## Три голосовые архитектуры

### Cascading

Streaming ASR → agent/LLM → streaming TTS. Плюсы: отдельная диагностика, зрелые компоненты, текстовые policy/tools, лёгкая замена этапа. Минусы: stage latency складывается, ASR теряет просодию/невербальные сигналы, ошибки передаются дальше.

Источники: `references/source-book/chapter9.md:42`, `references/source-book/chapter9.md:94`, `references/source-book/chapter9.md:106`.

### Omni

Одна модель принимает/выдаёт несколько модальностей. Плюсы: меньше жёстких промежуточных представлений, потенциально лучше эмоции и контекст. Минусы: слабее stage observability, сложнее policy/debugging и зависимость от capability конкретной модели.

Источник: `references/source-book/chapter9.md:149`.

### Full-Duplex

Модель одновременно слушает и говорит, управляет barge-in и turn-taking. Плюс — естественное взаимодействие. Риски — гонки между входом, generation, TTS и tools; cancellation и safety становятся частью протокола, а не UI-функцией.

Источник: `references/source-book/chapter9.md:174`.

## Выбор v1

Обычно начни с streaming Cascading, если нужны контролируемость и измеримость. Выбирай Omni при доказанном выигрыше на целевом языке/шуме/эмоциях и приемлемой observability. Full-Duplex требует зрелого state machine, streaming safety и race tests.

Если пользователь просит выбрать архитектуру, не ограничивайся названием победителя: дай компактную сравнительную таблицу Cascading/Omni/Full-Duplex с latency/observability/control trade-offs, затем зафиксируй v1 и условие пересмотра.

Не придумывай универсальный latency target. Составь stage budget из требований продукта и измерь p50/p95/p99: end-of-user-speech detection, first ASR hypothesis, decision, first safe audio, interruption stop и slow-task completion.

## Fast/slow architecture

Fast path поддерживает диалог: acknowledgement, clarification, короткий безопасный ответ и interruption. Slow path получает `turn_id`, `state_version`, evidence pointers, deadline, tool/cost budget и cancellation token. Он возвращает structured result с confidence/provenance.

Dispatcher публикует result только при актуальной версии. Stale result может быть сохранён как artifact, но не озвучен и не применён. Side effect должен иметь отдельную cancel/compensation policy.

Источники: `references/source-book/chapter9.md:192`, `references/source-book/chapter9.md:200`, `references/source-book/chapter9.md:220`, `references/source-book/chapter9.md:276`.

## Multimodal tools

Для TTS отделяй semantic response от speaking style. Для Computer Use action space должен быть ограничен и наблюдаем: screenshot/DOM/accessibility evidence, target grounding, precondition и post-action verification. Для robot control разделяй slow high-level planning и fast low-level safety/control loop; LLM не должен напрямую заменять жёсткий realtime controller.

Источники: `references/source-book/chapter9.md:288`, `references/source-book/chapter9.md:308`, `references/source-book/chapter9.md:327`, `references/source-book/chapter9.md:348`, `references/source-book/chapter9.md:418`, `references/source-book/chapter9.md:430`, `references/source-book/chapter9.md:450`.

## Антипаттерны

- Ждать полного slow reasoning перед любым feedback пользователю.
- Озвучивать result без проверки актуального turn/state.
- Считать остановку TTS отменой уже запущенного tool side effect.
- Оценивать только финальный answer, игнорируя interruption latency.
- Давать GUI agent координатный click без post-action observation.
- Управлять safety-critical actuator напрямую нерегулярным LLM loop.

## Eval

Тестируй шум, акцент, partial ASR correction, barge-in в разные моменты, overlapping speech, slow result after new turn, network jitter, tool timeout и unsafe utterance streaming. Метрики: first-audio latency, interruption-stop latency, word/intent accuracy, state consistency, stale-publication rate, side-effect correctness и user-rated naturalness. Все сравнения архитектур — на одинаковых сценариях и известном resource budget.
