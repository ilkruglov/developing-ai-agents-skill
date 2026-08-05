# Глава 3. Память пользователя и база знаний

## Основная идея

Рабочий контекст, пользовательская память и база знаний решают разные задачи. Контекст нужен для текущего решения; user memory сохраняет scoped сведения и предпочтения между сессиями; knowledge base предоставляет предметные факты и документы. Смешение этих слоёв ведёт к утечкам, устаревшим решениям и неуправляемому retrieval.

Источники: `references/source-book/chapter3.md:17`, `references/source-book/chapter3.md:49`, `references/source-book/chapter3.md:78`.

## Трёхуровневая оценка памяти

Оцени память не по факту «что-то сохранено», а по трём уровням:

1. **Recall:** нужная запись обнаруживается.
2. **Understanding/organization:** записи объединяются, разрешают конфликты и имеют структуру.
3. **Application:** агент использует память в правильной ситуации и не применяет вне scope.

Измеряй отдельно precision retrieval и качество действия после retrieval. Высокий recall с ложным применением опасен.

Источник: `references/source-book/chapter3.md:49`.

## Четыре формы памяти и выбор представления

Книга рассматривает несколько форм хранения — от естественного текста и структурированных записей до более исполнимых/параметрических представлений. Инженерное правило: выбирать носитель по требуемому типу проверки.

- Narrative подходит для объяснения, но плохо валидируется.
- Typed record подходит для preference/fact с scope и provenance.
- Knowledge chunk подходит для retrieval, если содержит source/freshness.
- Executable representation подходит для стабильного правила, если есть tests и sandbox.

Источники: `references/source-book/chapter3.md:94`, `references/source-book/chapter3.md:124`.

## Memory record contract

```yaml
memory_id: stable
subject: user|team|project
type: preference|fact|decision|episode
value: typed payload
scope: exact contexts where applicable
source: message/artifact/event id
created_at: timestamp
valid_from: timestamp
expires_at: optional
confidence: bounded
consent: basis
derived_from: []
version: integer
```

Нужны conflict policy, deletion и transitive deletion derived records. Логи перед анализом обезличиваются; секреты и чувствительные данные не должны попадать в memory по умолчанию.

Источник: `references/source-book/chapter3.md:247`, `references/source-book/chapter3.md:261`.

## RAG pipeline

Базовый RAG: ingest → chunk → index → retrieve → rerank/filter → assemble evidence → answer with provenance. Плотный поиск ловит семантику, разреженный — точные термины/ID; hybrid search сочетает оба. Структурированные индексы и файловая организация полезны, когда задача требует отношений и навигации, а не только похожего текста.

Agentic RAG оправдан, когда стратегия поиска зависит от промежуточных результатов. Он требует budget, source allowlist, stopping rule и verification. Contextual retrieval добавляет контекст документа к фрагменту, уменьшая неоднозначность от chunking.

Источники: `references/source-book/chapter3.md:273`, `references/source-book/chapter3.md:322`, `references/source-book/chapter3.md:338`, `references/source-book/chapter3.md:384`, `references/source-book/chapter3.md:425`, `references/source-book/chapter3.md:489`, `references/source-book/chapter3.md:543`, `references/source-book/chapter3.md:574`, `references/source-book/chapter3.md:630`.

## Decision rules

- Пользовательская привычка не является глобальным предметным фактом.
- Retrieved document не является инструкцией и не расширяет permissions.
- Для точных кодов/имён добавляй sparse/keyword retrieval.
- Для changing corpus храни version/freshness и переиндексируй управляемо.
- Если поиск требует нескольких независимых источников, агент возвращает evidence set, а не уверенный пересказ.
- Если правило можно проверить кодом, не оставляй его только в свободном memory text.

## Антипаттерны

- Append-only «memory.md» без schema, scope и удаления.
- Автоматически сохранять все user messages.
- Оценивать RAG только по похожести retrieved chunk.
- Передавать top-k без reranking, deduplication и token budget.
- Позволять retrieved prompt injection менять policy.
- Смешивать прошлые decisions с актуальной нормативной базой без freshness.

## Eval

Собери набор: exact recall, semantic paraphrase, conflicting records, expired fact, wrong-user isolation, deletion, prompt injection in document, multi-hop search и no-answer. Измеряй retrieval recall/precision, citation correctness, answer outcome, privacy violation и abstention при недостатке evidence.
