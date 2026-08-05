# Карта источников

Канонический источник skill — русская рукопись книги Bojie Li «AI-агенты изнутри: принципы проектирования и инженерная практика» в текущем репозитории. Перевод закреплён за upstream commit `97de455e9aa44cf9f93441ce0c771c9aa9643d92`; см. `README.md:9-13`. Книга и skill распространяются с учётом `LICENSE` (Apache-2.0).

Ссылки вида `references/source-book/chapterN.md:line` указывают на начало релевантного раздела. Все якоря зафиксированы в `references/source-map.lock.json` вместе с sha256 строки книги: расхождение обнаруживается валидатором, а не при чтении.

В большинстве случаев конспект главы отвечает на вопрос быстрее исходного текста: он содержит механизмы, таблицы решений и проверки. К исходной главе обращайся, когда нужна дословная формулировка.

| Тема | Первичный раздел | Конспект |
|---|---|---|
| Назначение и структура книги | `references/source-book/introduction.md:3`, `references/source-book/introduction.md:39`, `references/source-book/introduction.md:58` | `references/chapters/ch00-introduction.md` |
| Формула LLM + контекст + инструменты | `references/source-book/chapter1.md:13` | `references/chapters/ch01-agent-foundations.md` |
| ReAct | `references/source-book/chapter1.md:146` | `references/chapters/ch01-agent-foundations.md` |
| Harness-инженерия и пять функций | `references/source-book/chapter1.md:230`, `references/source-book/chapter1.md:272`, `references/source-book/chapter1.md:280` | `references/chapters/ch01-agent-foundations.md` |
| Простота, прозрачность, ACI, workflow/agent | `references/source-book/chapter1.md:295`, `references/source-book/chapter1.md:324` | `references/chapters/ch01-agent-foundations.md` |
| Guardrails и безопасность | `references/source-book/chapter1.md:387` | `references/chapters/ch01-agent-foundations.md` |
| Структура API-контекста | `references/source-book/chapter2.md:34`, `references/source-book/chapter2.md:355` | `references/chapters/ch02-context-engineering.md` |
| KV-cache как ограничение архитектуры | `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:524` | `references/chapters/ch02-context-engineering.md` |
| Prompt и tool definitions | `references/source-book/chapter2.md:560`, `references/source-book/chapter2.md:635` | `references/chapters/ch02-context-engineering.md` |
| Prompt injection | `references/source-book/chapter2.md:655` | `references/chapters/ch02-context-engineering.md` |
| Dynamic prompts и Skills | `references/source-book/chapter2.md:689`, `references/source-book/chapter2.md:700`, `references/source-book/chapter2.md:722` | `references/chapters/ch02-context-engineering.md` |
| Agent Status Bar | `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:842`, `references/source-book/chapter2.md:856` | `references/chapters/ch02-context-engineering.md` |
| Сжатие и изоляция контекста | `references/source-book/chapter2.md:936`, `references/source-book/chapter2.md:1017`, `references/source-book/chapter2.md:1054` | `references/chapters/ch02-context-engineering.md` |
| Трёхуровневая оценка памяти | `references/source-book/chapter3.md:49` | `references/chapters/ch03-memory-and-knowledge.md` |
| Иерархия и четыре формата памяти | `references/source-book/chapter3.md:78`, `references/source-book/chapter3.md:94` | `references/chapters/ch03-memory-and-knowledge.md` |
| Privacy памяти | `references/source-book/chapter3.md:261` | `references/chapters/ch03-memory-and-knowledge.md` |
| RAG, hybrid search, Agentic RAG | `references/source-book/chapter3.md:273`, `references/source-book/chapter3.md:425`, `references/source-book/chapter3.md:574` | `references/chapters/ch03-memory-and-knowledge.md` |
| Contextual retrieval | `references/source-book/chapter3.md:630` | `references/chapters/ch03-memory-and-knowledge.md` |
| Классы и проектирование tools | `references/source-book/chapter4.md:14`, `references/source-book/chapter4.md:41` | `references/chapters/ch04-tools.md` |
| MCP и выбор tools | `references/source-book/chapter4.md:110` | `references/chapters/ch04-tools.md` |
| Perception, execution, collaboration tools | `references/source-book/chapter4.md:147`, `references/source-book/chapter4.md:179`, `references/source-book/chapter4.md:284` | `references/chapters/ch04-tools.md` |
| Async/event-driven agent | `references/source-book/chapter4.md:347` | `references/chapters/ch04-tools.md` |
| Coding Agent, Sessionless, безопасность | `references/source-book/chapter5.md:15`, `references/source-book/chapter5.md:82`, `references/source-book/chapter5.md:92` | `references/chapters/ch05-coding-agents.md` |
| Harness и recovery Coding Agent | `references/source-book/chapter5.md:188`, `references/source-book/chapter5.md:233` | `references/chapters/ch05-coding-agents.md` |
| Code as meta-capability | `references/source-book/chapter5.md:354` | `references/chapters/ch05-coding-agents.md` |
| Evaluation environment и dataset | `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:157` | `references/chapters/ch06-evaluation.md` |
| Метрики и LLM-as-a-Judge | `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:284` | `references/chapters/ch06-evaluation.md` |
| Model/system selection и cost | `references/source-book/chapter6.md:421`, `references/source-book/chapter6.md:444` | `references/chapters/ch06-evaluation.md` |
| Statistics и observability | `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:534` | `references/chapters/ch06-evaluation.md` |
| Improvement loop, ablation, simulation | `references/source-book/chapter6.md:563`, `references/source-book/chapter6.md:635`, `references/source-book/chapter6.md:679` | `references/chapters/ch06-evaluation.md` |
| Pretraining/SFT/RL | `references/source-book/chapter7.md:27`, `references/source-book/chapter7.md:72`, `references/source-book/chapter7.md:305` | `references/chapters/ch07-post-training.md` |
| Data/environment before algorithm | `references/source-book/chapter7.md:447` | `references/chapters/ch07-post-training.md` |
| Multi-turn reward и RLVP | `references/source-book/chapter7.md:481`, `references/source-book/chapter7.md:581` | `references/chapters/ch07-post-training.md` |
| Tool-call RL и On-Policy Distillation | `references/source-book/chapter7.md:635`, `references/source-book/chapter7.md:694` | `references/chapters/ch07-post-training.md` |
| Три парадигмы обучения | `references/source-book/chapter8.md:23` | `references/chapters/ch08-self-evolution.md` |
| Experience, failures, Skills | `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`, `references/source-book/chapter8.md:113` | `references/chapters/ch08-self-evolution.md` |
| Prompt optimization и cross-session continuation | `references/source-book/chapter8.md:145`, `references/source-book/chapter8.md:181` | `references/chapters/ch08-self-evolution.md` |
| Tool discovery/creation | `references/source-book/chapter8.md:187`, `references/source-book/chapter8.md:236`, `references/source-book/chapter8.md:273` | `references/chapters/ch08-self-evolution.md` |
| Continuous accumulation и safety | `references/source-book/chapter8.md:319`, `references/source-book/chapter8.md:329` | `references/chapters/ch08-self-evolution.md` |
| Cascading, Omni, Full-Duplex | `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:42`, `references/source-book/chapter9.md:149`, `references/source-book/chapter9.md:174` | `references/chapters/ch09-realtime-multimodal.md` |
| Fast/slow thinking | `references/source-book/chapter9.md:192`, `references/source-book/chapter9.md:276` | `references/chapters/ch09-realtime-multimodal.md` |
| Computer Use и realtime | `references/source-book/chapter9.md:308`, `references/source-book/chapter9.md:418` | `references/chapters/ch09-realtime-multimodal.md` |
| Multi-agent: context/topology axes | `references/source-book/chapter10.md:11`, `references/source-book/chapter10.md:15`, `references/source-book/chapter10.md:53` | `references/chapters/ch10-multi-agent.md` |
| Когда multi-agent выигрывает | `references/source-book/chapter10.md:65` | `references/chapters/ch10-multi-agent.md` |
| Shared/no-shared context | `references/source-book/chapter10.md:94`, `references/source-book/chapter10.md:196` | `references/chapters/ch10-multi-agent.md` |
| Data/control planes и topologies | `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`, `references/source-book/chapter10.md:251`, `references/source-book/chapter10.md:287`, `references/source-book/chapter10.md:431` | `references/chapters/ch10-multi-agent.md` |
| File conflicts и cascading errors | `references/source-book/chapter10.md:481`, `references/source-book/chapter10.md:493`, `references/source-book/chapter10.md:511` | `references/chapters/ch10-multi-agent.md` |
| Возврат к основной формуле | `references/source-book/afterword.md:3` | `references/chapters/ch11-afterword.md` |

## Drift gate

Не используй книгу как подтверждение текущего статуса конкретного продукта. Перед утверждениями о существовании/доступности модели, API, SDK, MCP/A2A implementation, ценах, latency или context window:

1. найди текущую первичную документацию;
2. укажи дату/версию;
3. отдели факт от проектной inference;
4. если проверить нельзя, обозначь unknown и предложи измерение.
