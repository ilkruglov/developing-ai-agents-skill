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
| RAG, hybrid search, Agentic RAG | `references/source-book/chapter3.md:247`, `references/source-book/chapter3.md:389`, `references/source-book/chapter3.md:548` | `references/chapters/ch03-memory-and-knowledge.md` |
| Contextual retrieval | `references/source-book/chapter3.md:600` | `references/chapters/ch03-memory-and-knowledge.md` |
| Классы и проектирование tools | `references/source-book/chapter4.md:11`, `references/source-book/chapter4.md:38` | `references/chapters/ch04-tools.md` |
| MCP и выбор tools | `references/source-book/chapter4.md:104` | `references/chapters/ch04-tools.md` |
| Perception, execution, collaboration tools | `references/source-book/chapter4.md:230`, `references/source-book/chapter4.md:282`, `references/source-book/chapter4.md:398` | `references/chapters/ch04-tools.md` |
| Coding Agent, ядро универсального агента, безопасность | `references/source-book/chapter5.md:17`, `references/source-book/chapter5.md:65`, `references/source-book/chapter5.md:336` | `references/chapters/ch05-coding-agents.md` |
| Harness и recovery Coding Agent | `references/source-book/chapter5.md:134`, `references/source-book/chapter5.md:181` | `references/chapters/ch05-coding-agents.md` |
| Code as meta-capability | `references/source-book/chapter5.md:378` | `references/chapters/ch05-coding-agents.md` |
| Асинхронность и событийная архитектура | `references/source-book/chapter6.md:31`, `references/source-book/chapter6.md:77`, `references/source-book/chapter6.md:89`, `references/source-book/chapter6.md:119` | `references/chapters/ch06-interaction.md` |
| Виртуальная идентичность и изолированная среда | `references/source-book/chapter6.md:105` | `references/chapters/ch06-interaction.md` |
| Нативная асинхронность модели | `references/source-book/chapter6.md:206`, `references/source-book/chapter6.md:285`, `references/source-book/chapter6.md:299` | `references/chapters/ch06-interaction.md` |
| Cascading, Omni, Full-Duplex | `references/source-book/chapter6.md:323`, `references/source-book/chapter6.md:337`, `references/source-book/chapter6.md:402`, `references/source-book/chapter6.md:417` | `references/chapters/ch06-interaction.md` |
| Fast/slow thinking | `references/source-book/chapter6.md:429`, `references/source-book/chapter6.md:453` | `references/chapters/ch06-interaction.md` |
| Computer Use: grounding, наблюдение, модель мира | `references/source-book/chapter6.md:477`, `references/source-book/chapter6.md:515`, `references/source-book/chapter6.md:569`, `references/source-book/chapter6.md:577` | `references/chapters/ch06-interaction.md` |
| Роботы: планировщик навыков, VLA, мировая модель | `references/source-book/chapter6.md:606`, `references/source-book/chapter6.md:649`, `references/source-book/chapter6.md:689`, `references/source-book/chapter6.md:714` | `references/chapters/ch06-interaction.md` |
| Анатомия задачи, Pass@k и Pass^k | `references/source-book/chapter7.md:31`, `references/source-book/chapter7.md:136`, `references/source-book/chapter7.md:140`, `references/source-book/chapter7.md:154` | `references/chapters/ch07-evaluation.md` |
| Evaluation environment и dataset | `references/source-book/chapter7.md:169`, `references/source-book/chapter7.md:212`, `references/source-book/chapter7.md:293` | `references/chapters/ch07-evaluation.md` |
| Оценщики, задачи-ловушки, утечка | `references/source-book/chapter7.md:231`, `references/source-book/chapter7.md:245`, `references/source-book/chapter7.md:255` | `references/chapters/ch07-evaluation.md` |
| LLM-as-a-Judge и смещение в пользу длины | `references/source-book/chapter7.md:307`, `references/source-book/chapter7.md:331` | `references/chapters/ch07-evaluation.md` |
| Атрибуция неудач и регрессионные задачи | `references/source-book/chapter7.md:469`, `references/source-book/chapter7.md:499`, `references/source-book/chapter7.md:550` | `references/chapters/ch07-evaluation.md` |
| Model selection, поведенческая стратегия, cost | `references/source-book/chapter7.md:597`, `references/source-book/chapter7.md:627`, `references/source-book/chapter7.md:643` | `references/chapters/ch07-evaluation.md` |
| Statistics и observability | `references/source-book/chapter7.md:716`, `references/source-book/chapter7.md:746` | `references/chapters/ch07-evaluation.md` |
| Improvement loop и simulation | `references/source-book/chapter7.md:766`, `references/source-book/chapter7.md:877` | `references/chapters/ch07-evaluation.md` |
| Внутренняя инфраструктура оценки: абляция, A/B, флаги, промпты | `references/source-book/chapter7.md:827`, `references/source-book/chapter7.md:831`, `references/source-book/chapter7.md:837`, `references/source-book/chapter7.md:849`, `references/source-book/chapter7.md:861`, `references/source-book/chapter7.md:867` | `references/chapters/ch07-evaluation.md` |
| Четыре этапа: предобучение, Mid-training, SFT, RL | `references/source-book/chapter8.md:31`, `references/source-book/chapter8.md:58`, `references/source-book/chapter8.md:66`, `references/source-book/chapter8.md:115` | `references/chapters/ch08-post-training.md` |
| Mid-training и данные для него | `references/source-book/chapter8.md:325`, `references/source-book/chapter8.md:336` | `references/chapters/ch08-post-training.md` |
| SFT, синтез данных, порядок диагностики | `references/source-book/chapter8.md:365`, `references/source-book/chapter8.md:440`, `references/source-book/chapter8.md:458` | `references/chapters/ch08-post-training.md` |
| GRPO, on-policy, численные расхождения | `references/source-book/chapter8.md:582`, `references/source-book/chapter8.md:606`, `references/source-book/chapter8.md:619` | `references/chapters/ch08-post-training.md` |
| Среда RL и модель как среда | `references/source-book/chapter8.md:632`, `references/source-book/chapter8.md:652`, `references/source-book/chapter8.md:664` | `references/chapters/ch08-post-training.md` |
| Вознаграждение: источник, момент, объём; RLVP | `references/source-book/chapter8.md:676`, `references/source-book/chapter8.md:732`, `references/source-book/chapter8.md:736`, `references/source-book/chapter8.md:746`, `references/source-book/chapter8.md:772` | `references/chapters/ch08-post-training.md` |
| Дистилляция, On-Policy Distillation, OPSD | `references/source-book/chapter8.md:800`, `references/source-book/chapter8.md:812`, `references/source-book/chapter8.md:845` | `references/chapters/ch08-post-training.md` |
| От проблемных случаев к постобучению | `references/source-book/chapter8.md:869`, `references/source-book/chapter8.md:914` | `references/chapters/ch08-post-training.md` |
| Обучающие сигналы и трёхуровневая проверка | `references/source-book/chapter9.md:21` | `references/chapters/ch09-continual-evolution.md` |
| Четыре способа эволюции: знания, инструкции, программа, параметры | `references/source-book/chapter9.md:58`, `references/source-book/chapter9.md:262` | `references/chapters/ch09-continual-evolution.md` |
| Опыт в знания и в инструкции | `references/source-book/chapter9.md:77`, `references/source-book/chapter9.md:99`, `references/source-book/chapter9.md:145` | `references/chapters/ch09-continual-evolution.md` |
| Масштабы поиска, локальные патчи, два цикла | `references/source-book/chapter9.md:270`, `references/source-book/chapter9.md:300`, `references/source-book/chapter9.md:343` | `references/chapters/ch09-continual-evolution.md` |
| Опыт в программу, самомодифицирующийся Harness | `references/source-book/chapter4.md:137`, `references/source-book/chapter9.md:177`, `references/source-book/chapter9.md:238` | `references/chapters/ch09-continual-evolution.md` |
| Границы безопасности и обучение во сне | `references/source-book/chapter9.md:356`, `references/source-book/chapter9.md:366` | `references/chapters/ch09-continual-evolution.md` |
| Multi-agent: context/topology axes | `references/source-book/chapter10.md:13`, `references/source-book/chapter10.md:17`, `references/source-book/chapter10.md:36` | `references/chapters/ch10-multi-agent.md` |
| Когда multi-agent выигрывает | `references/source-book/chapter10.md:48` | `references/chapters/ch10-multi-agent.md` |
| Shared/no-shared context | `references/source-book/chapter10.md:89`, `references/source-book/chapter10.md:114` | `references/chapters/ch10-multi-agent.md` |
| Data/control planes и topologies | `references/source-book/chapter10.md:149`, `references/source-book/chapter10.md:186`, `references/source-book/chapter10.md:222`, `references/source-book/chapter10.md:322`, `references/source-book/chapter10.md:489` | `references/chapters/ch10-multi-agent.md` |
| File conflicts и cascading errors | `references/source-book/chapter10.md:579`, `references/source-book/chapter10.md:599`, `references/source-book/chapter10.md:615` | `references/chapters/ch10-multi-agent.md` |
| Возврат к основной формуле | `references/source-book/afterword.md:3` | `references/chapters/ch11-afterword.md` |
| Справочные ответы на вопросы для размышления | `references/source-book/reference-answers.md:7`, `references/source-book/reference-answers.md:300`, `references/source-book/reference-answers.md:348`, `references/source-book/reference-answers.md:422` | `references/chapters/ch12-reference-answers.md` |

## Drift gate

Не используй книгу как подтверждение текущего статуса конкретного продукта. Перед утверждениями о существовании/доступности модели, API, SDK, MCP/A2A implementation, ценах, latency или context window:

1. найди текущую первичную документацию;
2. укажи дату/версию;
3. отдели факт от проектной inference;
4. если проверить нельзя, обозначь unknown и предложи измерение.
