# Developing AI Agents Skill

Автономный русскоязычный Skill для проектирования, реализации, диагностики и
оценки production AI-агентов. Он охватывает context engineering, Harness,
tool contracts, memory/RAG, evaluation, post-training, self-evolution,
realtime interaction и multi-agent coordination.

Репозиторий полностью self-contained: необходимые текстовые источники книги,
инженерные конспекты, evals и offline-валидатор находятся внутри. Доступ к
исходному репозиторию книги во время работы Skill не требуется. Сеть нужна
только тогда, когда конкретная задача требует проверить изменяемые внешние
факты: API, SDK, модели, цены, лимиты или поддержку провайдера.

## Установка

В проект:

```bash
git clone https://github.com/ilkruglov/developing-ai-agents-skill.git \
  .agents/skills/developing-ai-agents
```

В личный каталог Codex:

```bash
git clone https://github.com/ilkruglov/developing-ai-agents-skill.git \
  ~/.codex/skills/developing-ai-agents
```

После установки попросите агента использовать `$developing-ai-agents` либо
задайте задачу по архитектуре, отладке или evaluation AI-агента — описание в
`SKILL.md` предназначено и для автоматического triggering.

## Проверка

Валидатор использует только Python standard library:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Он проверяет структуру Skill, frontmatter, локальные книжные anchors,
Markdown-ссылки, JSON/JSONL и обязательную атрибуцию.

## Benchmark v2

Локальный held-out benchmark: 12 сценариев, 3 повтора, 72 ответа, отдельный
grading и 36 слепых A/B-сравнений.

| Метрика | Со Skill | Baseline |
|---|---:|---:|
| Assertion pass rate | 90,0% (162/180) | 75,0% (135/180) |
| Blind A/B wins | 28/36 | 8/36 |
| Trigger precision / recall | 100% / 100% | — |

Полные формальные результаты и ограничения методики находятся в
[`benchmarks/v2/`](benchmarks/v2/). Точная runner-модель, token и time
telemetry не были записаны; задачи внутри одного runner-контекста не полностью
независимы.

## Структура

- `SKILL.md` — основной рабочий контракт.
- `references/` — инженерные конспекты, patterns, glossary и локальные источники.
- `references/source-book/` — 12 русских Markdown-глав, используемых anchors.
- `evals/` — eval-наборы и воспроизводимые fixtures.
- `benchmarks/v2/` — результаты полного benchmark.
- `scripts/validate.py` — автономная проверка репозитория.

## Автор и источники

Skill основан на книге Bojie Li «深入理解 AI Agent：设计原理与工程实践»:

- автор: [Bojie Li](https://github.com/bojieli);
- оригинальная книга: [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book);
- русский перевод: [ilkruglov/ai-agent-book](https://github.com/ilkruglov/ai-agent-book),
  «Русский перевод: community edition».

Точные версии источников записаны в [`SOURCE.json`](SOURCE.json), а сведения о
производном произведении — в [`NOTICE`](NOTICE).

## Лицензия

Apache License 2.0. См. [`LICENSE`](LICENSE).
