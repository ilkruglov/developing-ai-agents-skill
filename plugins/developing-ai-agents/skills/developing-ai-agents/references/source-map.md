# Карта источников

Канонический источник skill — русская рукопись книги Bojie Li «AI-агенты изнутри: принципы проектирования и инженерная практика» в текущем репозитории. Перевод соответствует второй редакции книги (v2.0), upstream commit `c3352738f4b6fe42fe34e3cf6a79bcb424a133b8`; пины перевода и оригинала — в `SOURCE.json`. Книга и skill распространяются с учётом `LICENSE` (Apache-2.0).

Ссылки вида `references/source-book/chapterN.md:line` указывают на начало релевантного раздела. Все якоря зафиксированы в `references/source-map.lock.json` вместе с sha256 строки книги: расхождение обнаруживается валидатором, а не при чтении.

В большинстве случаев конспект главы отвечает на вопрос быстрее исходного текста: он содержит механизмы, таблицы решений и проверки. К исходной главе обращайся, когда нужна дословная формулировка.

| Тема | Первичный раздел | Конспект |
|---|---|---|
| Назначение и структура книги | `references/source-book/introduction.md:3`, `references/source-book/introduction.md:39`, `references/source-book/introduction.md:56` | `references/chapters/ch00-introduction.md` |
| Формула LLM + контекст + инструменты | `references/source-book/chapter1.md:13` | `references/chapters/ch01-agent-foundations.md` |
| ReAct | `references/source-book/chapter1.md:164` | `references/chapters/ch01-agent-foundations.md` |
| Harness-инженерия и пять функций | `references/source-book/chapter1.md:266`, `references/source-book/chapter1.md:324`, `references/source-book/chapter1.md:509` | `references/chapters/ch01-agent-foundations.md` |
| Простота, прозрачность, ACI, workflow/agent | `references/source-book/chapter1.md:344`, `references/source-book/chapter1.md:375` | `references/chapters/ch01-agent-foundations.md` |
| Guardrails и безопасность | `references/source-book/chapter1.md:469` | `references/chapters/ch01-agent-foundations.md` |
| Структура API-контекста | `references/source-book/chapter2.md:43`, `references/source-book/chapter2.md:372` | `references/chapters/ch02-context-engineering.md` |
| KV-cache как ограничение архитектуры | `references/source-book/chapter2.md:437`, `references/source-book/chapter2.md:562` | `references/chapters/ch02-context-engineering.md` |
| Prompt и tool definitions | `references/source-book/chapter2.md:604`, `references/source-book/chapter2.md:702` | `references/chapters/ch02-context-engineering.md` |
| Prompt injection | `references/source-book/chapter2.md:732` | `references/chapters/ch02-context-engineering.md` |
| Dynamic prompts и Skills | `references/source-book/chapter2.md:767`, `references/source-book/chapter2.md:778`, `references/source-book/chapter2.md:816` | `references/chapters/ch02-context-engineering.md` |
| Agent Status Bar | `references/source-book/chapter2.md:860`, `references/source-book/chapter2.md:911`, `references/source-book/chapter2.md:923` | `references/chapters/ch02-context-engineering.md` |
| Сжатие и изоляция контекста | `references/source-book/chapter2.md:994`, `references/source-book/chapter2.md:1069`, `references/source-book/chapter2.md:1092` | `references/chapters/ch02-context-engineering.md` |
| Трёхуровневая оценка памяти | `references/source-book/chapter3.md:47` | `references/chapters/ch03-memory-and-knowledge.md` |
| Иерархия и четыре формата памяти | `references/source-book/chapter3.md:76`, `references/source-book/chapter3.md:92` | `references/chapters/ch03-memory-and-knowledge.md` |
| Privacy памяти | `references/source-book/chapter3.md:235` | `references/chapters/ch03-memory-and-knowledge.md` |
| RAG, hybrid search, Agentic RAG | `references/source-book/chapter3.md:247`, `references/source-book/chapter3.md:389`, `references/source-book/chapter3.md:546` | `references/chapters/ch03-memory-and-knowledge.md` |
| Contextual retrieval | `references/source-book/chapter3.md:598` | `references/chapters/ch03-memory-and-knowledge.md` |
| Классы и проектирование tools | `references/source-book/chapter4.md:9`, `references/source-book/chapter4.md:36` | `references/chapters/ch04-tools.md` |
| MCP и выбор tools | `references/source-book/chapter4.md:102` | `references/chapters/ch04-tools.md` |
| Perception, execution, collaboration tools | `references/source-book/chapter4.md:220`, `references/source-book/chapter4.md:272`, `references/source-book/chapter4.md:384` | `references/chapters/ch04-tools.md` |
| Coding Agent, ядро универсального агента, безопасность | `references/source-book/chapter5.md:15`, `references/source-book/chapter5.md:60`, `references/source-book/chapter5.md:311` | `references/chapters/ch05-coding-agents.md` |
| Harness и recovery Coding Agent | `references/source-book/chapter5.md:129`, `references/source-book/chapter5.md:174` | `references/chapters/ch05-coding-agents.md` |
| Code as meta-capability | `references/source-book/chapter5.md:353` | `references/chapters/ch05-coding-agents.md` |
| Асинхронность и событийная архитектура | `references/source-book/chapter6.md:31`, `references/source-book/chapter6.md:75`, `references/source-book/chapter6.md:87`, `references/source-book/chapter6.md:115` | `references/chapters/ch06-interaction.md` |
| Виртуальная идентичность и изолированная среда | `references/source-book/chapter6.md:103` | `references/chapters/ch06-interaction.md` |
| Нативная асинхронность модели | `references/source-book/chapter6.md:200`, `references/source-book/chapter6.md:277`, `references/source-book/chapter6.md:291` | `references/chapters/ch06-interaction.md` |
| Cascading, Omni, Full-Duplex | `references/source-book/chapter6.md:315`, `references/source-book/chapter6.md:329`, `references/source-book/chapter6.md:391`, `references/source-book/chapter6.md:406` | `references/chapters/ch06-interaction.md` |
| Fast/slow thinking | `references/source-book/chapter6.md:418`, `references/source-book/chapter6.md:440` | `references/chapters/ch06-interaction.md` |
| Computer Use: grounding, наблюдение, модель мира | `references/source-book/chapter6.md:462`, `references/source-book/chapter6.md:500`, `references/source-book/chapter6.md:550`, `references/source-book/chapter6.md:558` | `references/chapters/ch06-interaction.md` |
| Роботы: планировщик навыков, VLA, мировая модель | `references/source-book/chapter6.md:587`, `references/source-book/chapter6.md:626`, `references/source-book/chapter6.md:666`, `references/source-book/chapter6.md:691` | `references/chapters/ch06-interaction.md` |
| Анатомия задачи, Pass@k и Pass^k | `references/source-book/chapter7.md:29`, `references/source-book/chapter7.md:132`, `references/source-book/chapter7.md:136`, `references/source-book/chapter7.md:150` | `references/chapters/ch07-evaluation.md` |
| Evaluation environment и dataset | `references/source-book/chapter7.md:165`, `references/source-book/chapter7.md:206`, `references/source-book/chapter7.md:277` | `references/chapters/ch07-evaluation.md` |
| Оценщики, задачи-ловушки, утечка | `references/source-book/chapter7.md:225`, `references/source-book/chapter7.md:235`, `references/source-book/chapter7.md:245` | `references/chapters/ch07-evaluation.md` |
| LLM-as-a-Judge и смещение в пользу длины | `references/source-book/chapter7.md:291`, `references/source-book/chapter7.md:307` | `references/chapters/ch07-evaluation.md` |
| Атрибуция неудач и регрессионные задачи | `references/source-book/chapter7.md:437`, `references/source-book/chapter7.md:467`, `references/source-book/chapter7.md:516` | `references/chapters/ch07-evaluation.md` |
| Model selection, поведенческая стратегия, cost | `references/source-book/chapter7.md:561`, `references/source-book/chapter7.md:586`, `references/source-book/chapter7.md:602` | `references/chapters/ch07-evaluation.md` |
| Statistics и observability | `references/source-book/chapter7.md:675`, `references/source-book/chapter7.md:701` | `references/chapters/ch07-evaluation.md` |
| Improvement loop и simulation | `references/source-book/chapter7.md:721`, `references/source-book/chapter7.md:828` | `references/chapters/ch07-evaluation.md` |
| Внутренняя инфраструктура оценки: абляция, A/B, флаги, промпты | `references/source-book/chapter7.md:780`, `references/source-book/chapter7.md:784`, `references/source-book/chapter7.md:790`, `references/source-book/chapter7.md:802`, `references/source-book/chapter7.md:812`, `references/source-book/chapter7.md:818` | `references/chapters/ch07-evaluation.md` |
| Четыре этапа: предобучение, Mid-training, SFT, RL | `references/source-book/chapter8.md:28`, `references/source-book/chapter8.md:51`, `references/source-book/chapter8.md:57`, `references/source-book/chapter8.md:88` | `references/chapters/ch08-post-training.md` |
| Mid-training и данные для него | `references/source-book/chapter8.md:278`, `references/source-book/chapter8.md:289` | `references/chapters/ch08-post-training.md` |
| SFT, синтез данных, порядок диагностики | `references/source-book/chapter8.md:316`, `references/source-book/chapter8.md:371`, `references/source-book/chapter8.md:387` | `references/chapters/ch08-post-training.md` |
| GRPO, on-policy, численные расхождения | `references/source-book/chapter8.md:485`, `references/source-book/chapter8.md:507`, `references/source-book/chapter8.md:520` | `references/chapters/ch08-post-training.md` |
| Среда RL и модель как среда | `references/source-book/chapter8.md:533`, `references/source-book/chapter8.md:547`, `references/source-book/chapter8.md:557` | `references/chapters/ch08-post-training.md` |
| Вознаграждение: источник, момент, объём; RLVP | `references/source-book/chapter8.md:567`, `references/source-book/chapter8.md:613`, `references/source-book/chapter8.md:617`, `references/source-book/chapter8.md:627`, `references/source-book/chapter8.md:647` | `references/chapters/ch08-post-training.md` |
| Дистилляция, On-Policy Distillation, OPSD | `references/source-book/chapter8.md:673`, `references/source-book/chapter8.md:681`, `references/source-book/chapter8.md:714` | `references/chapters/ch08-post-training.md` |
| От проблемных случаев к постобучению | `references/source-book/chapter8.md:736`, `references/source-book/chapter8.md:781` | `references/chapters/ch08-post-training.md` |
| Обучающие сигналы и трёхуровневая проверка | `references/source-book/chapter9.md:21` | `references/chapters/ch09-continual-evolution.md` |
| Четыре способа эволюции: знания, инструкции, программа, параметры | `references/source-book/chapter9.md:58`, `references/source-book/chapter9.md:252` | `references/chapters/ch09-continual-evolution.md` |
| Опыт в знания и в инструкции | `references/source-book/chapter9.md:77`, `references/source-book/chapter9.md:99`, `references/source-book/chapter9.md:137` | `references/chapters/ch09-continual-evolution.md` |
| Масштабы поиска, локальные патчи, два цикла | `references/source-book/chapter9.md:260`, `references/source-book/chapter9.md:290`, `references/source-book/chapter9.md:333` | `references/chapters/ch09-continual-evolution.md` |
| Опыт в программу, самомодифицирующийся Harness | `references/source-book/chapter4.md:135`, `references/source-book/chapter9.md:169`, `references/source-book/chapter9.md:230` | `references/chapters/ch09-continual-evolution.md` |
| Границы безопасности и обучение во сне | `references/source-book/chapter9.md:346`, `references/source-book/chapter9.md:356` | `references/chapters/ch09-continual-evolution.md` |
| Multi-agent: context/topology axes | `references/source-book/chapter10.md:13`, `references/source-book/chapter10.md:17`, `references/source-book/chapter10.md:36` | `references/chapters/ch10-multi-agent.md` |
| Когда multi-agent выигрывает | `references/source-book/chapter10.md:48` | `references/chapters/ch10-multi-agent.md` |
| Shared/no-shared context | `references/source-book/chapter10.md:81`, `references/source-book/chapter10.md:104` | `references/chapters/ch10-multi-agent.md` |
| Data/control planes и topologies | `references/source-book/chapter10.md:135`, `references/source-book/chapter10.md:168`, `references/source-book/chapter10.md:196`, `references/source-book/chapter10.md:286`, `references/source-book/chapter10.md:445` | `references/chapters/ch10-multi-agent.md` |
| File conflicts и cascading errors | `references/source-book/chapter10.md:525`, `references/source-book/chapter10.md:539`, `references/source-book/chapter10.md:551` | `references/chapters/ch10-multi-agent.md` |
| Возврат к основной формуле | `references/source-book/afterword.md:3` | `references/chapters/ch11-afterword.md` |
| Справочные ответы на вопросы для размышления | `references/source-book/reference-answers.md:7`, `references/source-book/reference-answers.md:246`, `references/source-book/reference-answers.md:286`, `references/source-book/reference-answers.md:340` | `references/chapters/ch12-reference-answers.md` |

## Drift gate

Не используй книгу как подтверждение текущего статуса конкретного продукта. Перед утверждениями о существовании/доступности модели, API, SDK, MCP/A2A implementation, ценах, latency или context window:

1. найди текущую первичную документацию;
2. укажи дату/версию;
3. отдели факт от проектной inference;
4. если проверить нельзя, обозначь unknown и предложи измерение.
