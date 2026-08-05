# Карта источников

Канонический источник skill — русская рукопись книги Bojie Li «AI-агенты изнутри: принципы проектирования и инженерная практика» в текущем репозитории. Перевод закреплён за upstream commit `97de455e9aa44cf9f93441ce0c771c9aa9643d92`; см. `README.md:9-13`. Книга и skill распространяются с учётом `LICENSE` (Apache-2.0).

Ссылки вида `references/source-book/chapterN.md:line` указывают на начало релевантного раздела, а не на единственную строку-доказательство. При изменении рукописи перепроверь номера строк.

| Тема | Первичный раздел |
|---|---|
| Назначение и структура книги | `references/source-book/introduction.md:3`, `references/source-book/introduction.md:39`, `references/source-book/introduction.md:58` |
| Формула LLM + контекст + инструменты | `references/source-book/chapter1.md:13` |
| ReAct | `references/source-book/chapter1.md:146` |
| Harness-инженерия и пять функций | `references/source-book/chapter1.md:230`, `references/source-book/chapter1.md:272`, `references/source-book/chapter1.md:280` |
| Простота, прозрачность, ACI, workflow/agent | `references/source-book/chapter1.md:295`, `references/source-book/chapter1.md:324` |
| Guardrails и безопасность | `references/source-book/chapter1.md:387` |
| Структура API-контекста | `references/source-book/chapter2.md:34`, `references/source-book/chapter2.md:355` |
| KV-cache как ограничение архитектуры | `references/source-book/chapter2.md:401`, `references/source-book/chapter2.md:524` |
| Prompt и tool definitions | `references/source-book/chapter2.md:560`, `references/source-book/chapter2.md:635` |
| Prompt injection | `references/source-book/chapter2.md:655` |
| Dynamic prompts и Skills | `references/source-book/chapter2.md:689`, `references/source-book/chapter2.md:700`, `references/source-book/chapter2.md:722` |
| Agent Status Bar | `references/source-book/chapter2.md:763`, `references/source-book/chapter2.md:842`, `references/source-book/chapter2.md:856` |
| Сжатие и изоляция контекста | `references/source-book/chapter2.md:936`, `references/source-book/chapter2.md:1017`, `references/source-book/chapter2.md:1054` |
| Трёхуровневая оценка памяти | `references/source-book/chapter3.md:49` |
| Иерархия и четыре формата памяти | `references/source-book/chapter3.md:78`, `references/source-book/chapter3.md:94` |
| Privacy памяти | `references/source-book/chapter3.md:261` |
| RAG, hybrid search, Agentic RAG | `references/source-book/chapter3.md:273`, `references/source-book/chapter3.md:425`, `references/source-book/chapter3.md:574` |
| Contextual retrieval | `references/source-book/chapter3.md:630` |
| Классы и проектирование tools | `references/source-book/chapter4.md:14`, `references/source-book/chapter4.md:41` |
| MCP и выбор tools | `references/source-book/chapter4.md:110` |
| Perception, execution, collaboration tools | `references/source-book/chapter4.md:147`, `references/source-book/chapter4.md:179`, `references/source-book/chapter4.md:284` |
| Async/event-driven agent | `references/source-book/chapter4.md:347` |
| Coding Agent, Sessionless, безопасность | `references/source-book/chapter5.md:15`, `references/source-book/chapter5.md:82`, `references/source-book/chapter5.md:92` |
| Harness и recovery Coding Agent | `references/source-book/chapter5.md:188`, `references/source-book/chapter5.md:233` |
| Code as meta-capability | `references/source-book/chapter5.md:354` |
| Evaluation environment и dataset | `references/source-book/chapter6.md:71`, `references/source-book/chapter6.md:157` |
| Метрики и LLM-as-a-Judge | `references/source-book/chapter6.md:239`, `references/source-book/chapter6.md:284` |
| Model/system selection и cost | `references/source-book/chapter6.md:421`, `references/source-book/chapter6.md:444` |
| Statistics и observability | `references/source-book/chapter6.md:520`, `references/source-book/chapter6.md:534` |
| Improvement loop, ablation, simulation | `references/source-book/chapter6.md:563`, `references/source-book/chapter6.md:635`, `references/source-book/chapter6.md:679` |
| Pretraining/SFT/RL | `references/source-book/chapter7.md:27`, `references/source-book/chapter7.md:72`, `references/source-book/chapter7.md:305` |
| Data/environment before algorithm | `references/source-book/chapter7.md:447` |
| Multi-turn reward и RLVP | `references/source-book/chapter7.md:481`, `references/source-book/chapter7.md:581` |
| Tool-call RL и On-Policy Distillation | `references/source-book/chapter7.md:635`, `references/source-book/chapter7.md:694` |
| Три парадигмы обучения | `references/source-book/chapter8.md:23` |
| Experience, failures, Skills | `references/source-book/chapter8.md:53`, `references/source-book/chapter8.md:105`, `references/source-book/chapter8.md:113` |
| Prompt optimization и cross-session continuation | `references/source-book/chapter8.md:145`, `references/source-book/chapter8.md:181` |
| Tool discovery/creation | `references/source-book/chapter8.md:187`, `references/source-book/chapter8.md:236`, `references/source-book/chapter8.md:273` |
| Continuous accumulation и safety | `references/source-book/chapter8.md:319`, `references/source-book/chapter8.md:329` |
| Cascading, Omni, Full-Duplex | `references/source-book/chapter9.md:28`, `references/source-book/chapter9.md:42`, `references/source-book/chapter9.md:149`, `references/source-book/chapter9.md:174` |
| Fast/slow thinking | `references/source-book/chapter9.md:192`, `references/source-book/chapter9.md:276` |
| Computer Use и realtime | `references/source-book/chapter9.md:308`, `references/source-book/chapter9.md:418` |
| Multi-agent: context/topology axes | `references/source-book/chapter10.md:11`, `references/source-book/chapter10.md:15`, `references/source-book/chapter10.md:53` |
| Когда multi-agent выигрывает | `references/source-book/chapter10.md:65` |
| Shared/no-shared context | `references/source-book/chapter10.md:94`, `references/source-book/chapter10.md:196` |
| Data/control planes и topologies | `references/source-book/chapter10.md:206`, `references/source-book/chapter10.md:237`, `references/source-book/chapter10.md:251`, `references/source-book/chapter10.md:287`, `references/source-book/chapter10.md:431` |
| File conflicts и cascading errors | `references/source-book/chapter10.md:481`, `references/source-book/chapter10.md:493`, `references/source-book/chapter10.md:511` |
| Возврат к основной формуле | `references/source-book/afterword.md:3` |

## Drift gate

Не используй книгу как подтверждение текущего статуса конкретного продукта. Перед утверждениями о существовании/доступности модели, API, SDK, MCP/A2A implementation, ценах, latency или context window:

1. найди текущую первичную документацию;
2. укажи дату/версию;
3. отдели факт от проектной inference;
4. если проверить нельзя, обозначь unknown и предложи измерение.
