# Глава 7. Постобучение модели

## Основная идея

Не каждую проблему агента нужно решать изменением весов. Context, tool, Harness и data/environment defects часто дешевле и надёжнее исправить на системном уровне. Post-training оправдан, когда нужное поведение должно устойчиво обобщаться на распределении задач и не может быть обеспечено контекстом/инструментом.

Источники: `references/source-book/chapter7.md:27`, `references/source-book/chapter7.md:305`.

## Pretraining, SFT, RL

- **Pretraining** формирует общие представления через next-token prediction на широких данных.
- **SFT** продолжает next-token training на demonstrations нужного поведения; хорошо передаёт format/style/policy exemplars.
- **RL** оптимизирует reward через взаимодействие/выбор trajectories; полезен, когда outcome можно оценить и требуется исследование действий.

SFT обычно предшествует RL, создавая приемлемую policy и формат действий. SFT и RL решают разные задачи; выбор начинается с данных и сигнала, а не с названия алгоритма.

Источники: `references/source-book/chapter7.md:39`, `references/source-book/chapter7.md:49`, `references/source-book/chapter7.md:62`, `references/source-book/chapter7.md:72`, `references/source-book/chapter7.md:264`.

## Decision rules

Используй SFT, если есть качественные demonstrations и нужно воспроизводить способ ответа/действия. Используй preference methods, если есть надёжные сравнительные предпочтения. Используй RL, если среда выдаёт проверяемый outcome, задача многошаговая и exploration действительно нужен.

Не начинай training, пока не доказано:

- что ошибка не вызвана missing context или broken tool;
- что environment воспроизводима;
- что reward не поощряет shortcut;
- что данные покрывают нужное распределение;
- что holdout и safety eval отделены.

Источник: `references/source-book/chapter7.md:305`, `references/source-book/chapter7.md:447`, `references/source-book/chapter7.md:461`, `references/source-book/chapter7.md:477`.

## Multi-turn credit assignment

Long-horizon agent получает outcome после многих шагов. Reward за каждый «красивый» шаг может мешать поиску сильной траектории; только финальный reward бывает слишком редким. Разделяй:

- outcome reward;
- проверяемые process constraints/penalties;
- dense intermediate signals, если они не меняют цель.

RLVP-идея: вознаграждать результат и отдельно ограничивать проверяемые нежелательные свойства trajectory. Не награждай chain-of-thought за сходство с эталоном, если множество стратегий валидно.

Источники: `references/source-book/chapter7.md:481`, `references/source-book/chapter7.md:493`, `references/source-book/chapter7.md:545`, `references/source-book/chapter7.md:581`.

## Tool-call training

Training environment должна исполнять реальные или достаточно точные tools, возвращать structured results и учитывать invalid schema, permission denial, retries и costs. Offline imitation успешных calls не учит восстановлению после нового observation. Защищай environment от reward hacking и симуляторных shortcut.

Источник: `references/source-book/chapter7.md:635`.

## On-Policy Distillation

Подход соединяет сильный teacher signal с trajectories текущей student policy. Практическая ценность — данные ближе к состояниям, которые реально посещает обучаемая модель, чем статический набор demonstrations. Требуются контроль teacher leakage/cost, versioning и честный holdout.

Источник: `references/source-book/chapter7.md:694`.

## Антипаттерны

- Fine-tune, чтобы компенсировать отсутствующий tool result.
- Reward по judge, который предпочитает длину, без калибровки.
- Обучать и оценивать в одном simulator distribution.
- Давать process reward за конкретную формулировку рассуждения.
- Сравнивать post-trained model при другом Harness и приписывать эффект весам.
- Переходить к RL без качественной environment/data pipeline.

## Eval

Проводи component ablation: base model + fixed Harness против post-trained model + того же Harness. Мерь outcome, constraint violations, tool trajectories, calibration, generalization, cost и regression на исходных возможностях. Отдельно тестируй environment shift и adversarial reward hacking.
