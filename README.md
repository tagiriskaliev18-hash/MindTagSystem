# MindTagSystem

**MindTagSystem** — экосистема программ, которую создаёт **Тагир Искалиев** ([@tagiriskaliev18-hash](https://github.com/tagiriskaliev18-hash)). Своя операционная система, свой браузер, своя IDE, своё ИИ-ядро и приложения поверх них, собранные так, чтобы работать вместе.

> **Философия.** Сделать максимально комфортную систему для программистов, которую можно встроить в любое устройство и сразу начать работать. Сегодня это компьютеры и ноутбуки, дальше планшеты и телефоны.

Это главный репозиторий экосистемы: карта, правила, описание того, как всё устроено, и **MindKit** — общие службы, которые связывают проекты так, как Apple связывает свои устройства. Сами проекты живут в своих репозиториях, и каждый из них ссылается сюда.

## Как у Apple: всё работает вместе

| У Apple | В MindTagSystem |
|---|---|
| Связка ключей | **Связка ключей Mind**: ключ API вводится один раз и виден всем проектам |
| Универсальный буфер, Handoff, AirDrop | **MindLink**: общий буфер обмена, Handoff вкладок, файлов и разговоров с ИИ, **MindDrop** |
| Spotlight | **Mind Search**: приложения, команды, Handoff и файлы проектов в одном поиске (и в KRunner AIsktagOS) |
| Siri и Команды | **Ассистент Mind** (`mindkit ask`) и **быстрые команды** |
| App Store | **Mind Store**: все приложения экосистемы ставятся и обновляются одной командой |
| Human Interface Guidelines | **Дизайн Aurora**: одни токены для веба и Qt |

```bash
pip install "mindkit[full] @ git+https://github.com/tagiriskaliev18-hash/MindTagSystem"
mindkit status
```

Подробно: [docs/APPLE.md](docs/APPLE.md) (какие фишки Apple уже есть и что дальше) и [docs/MINDKIT.md](docs/MINDKIT.md) (как пользоваться).

## Проекты

| Слой | Проект | Что делает | Статус |
|---|---|---|---|
| Платформа | **[AIsktagOS](https://github.com/tagiriskaliev18-hash/AisktagOS)** | Операционная система для разработчиков в стиле macOS на базе Ubuntu 26.04 LTS. Любое x86-64 железо и любая видеокарта, инструменты программиста из коробки | 1.0, ISO в Releases |
| Инструменты | **[Mind IDE](https://github.com/tagiriskaliev18-hash/Mind-IDE)** | Собственная ИИ-среда разработки: один чат с моделями, Claude Code и Antigravity, автоматический выбор модели под задачу | работает на Windows, встраивается в AIsktagOS |
| Инструменты | **[ITIS Browser](https://github.com/tagiriskaliev18-hash/ITIS-browser)** | Браузер на Chromium с ИИ-агентом, который читает страницу и сам кликает и прокручивает её | прототип |
| ИИ-ядро | **[AI Duo / multimodel-agent](https://github.com/tagiriskaliev18-hash/multimodel-agent)** | Единый ИИ-шлюз с OpenAI-совместимым API поверх OpenAI, Hermes, Groq, Ollama и Pollinations | работает, Docker |
| ИИ-ядро | **[antigravity-claude-bridge](https://github.com/tagiriskaliev18-hash/antigravity-claude-bridge)** | MCP-мост между Antigravity (Gemini), Claude Code и пулом внешних моделей | используется ежедневно |
| ИИ-ядро | **[qwen14b-coder-dev](https://github.com/tagiriskaliev18-hash/qwen14b-coder-dev)** | Локальная офлайн-модель для программирования (Qwen 2.5 Coder 14B в Ollama) с веб-чатом | работает |
| Приложения | **[MindMail](https://github.com/tagiriskaliev18-hash/MindMail)** | Своя почта: Gmail, Mail.ru, Яндекс, Outlook и любой IMAP в одних входящих, плюс лучшее из каждой службы — вкладки, отмена и отложенная отправка, отписка в один клик, ИИ-помощник Mind | 0.1, работает |
| Приложения | **[FileHub AI](https://github.com/tagiriskaliev18-hash/filehub-ai)** | Хранилище файлов с ИИ-агентом, который правит Word, PowerPoint и Excel по тексту, плюс сжатие и конвертация | MVP |
| Приложения | **[SortApp](https://github.com/tagiriskaliev18-hash/sortapp)** | Анализатор журналов доступа к сетевым папкам Synology с отчётами Excel (закрытый репозиторий) | в работе |
| Приложения | **[ИИ Доктор](https://github.com/tagiriskaliev18-hash/medical-ai-assistant)** | Офлайн-ассистент врача приёмного покоя: калькуляторы, анализы, лекарства, протоколы SOAP | работает |

Подробно о каждом проекте: [docs/PROJECTS.md](docs/PROJECTS.md). Машиночитаемый реестр: [ecosystem.json](ecosystem.json).

## Как устроена экосистема

```mermaid
flowchart TB
    subgraph L1["Платформа"]
        OS["AIsktagOS<br/>ОС для разработчиков"]
    end
    subgraph L2["Инструменты разработчика"]
        IDE["Mind IDE"]
        BR["ITIS Browser"]
    end
    subgraph L3["ИИ-ядро"]
        GW["AI Duo<br/>multimodel-agent<br/>OpenAI-совместимый шлюз"]
        BRIDGE["antigravity-claude-bridge<br/>MCP-мост агентов"]
        QWEN["qwen14b-coder-dev<br/>локальная модель"]
    end
    subgraph L4["Приложения"]
        MM["MindMail"]
        FH["FileHub AI"]
        SA["SortApp"]
        MED["ИИ Доктор"]
    end

    OS --> IDE & BR
    OS -- "Ollama и Claude Code ставятся в один клик" --> QWEN & BRIDGE
    IDE --> BRIDGE
    BRIDGE --> GW
    GW -- "Ollama" --> QWEN
    BR -. "OpenAI-совместимый API" .-> GW
    FH -. "LOCALAI_BASE_URL" .-> GW
    MED -. "LLM_BASE_URL" .-> GW
    MM -. "ИИ-помощник" .-> GW
```

Четыре слоя, снизу вверх:

1. **Платформа.** AIsktagOS даёт стабильную основу: одна и та же среда на любом компьютере, всё для разработки уже стоит.
2. **Инструменты разработчика.** Mind IDE и ITIS Browser: где программист пишет код и работает с вебом.
3. **ИИ-ядро.** Модели и маршрутизация. Локальная модель работает без интернета, шлюз объединяет облачные и локальные модели за одним API, мост позволяет нескольким агентам работать над одной задачей.
4. **Приложения.** Готовые продукты для людей и компаний, которые используют ИИ-ядро.

Сплошные стрелки на схеме работают уже сейчас. Пунктирные показывают подключение, которое уже возможно через настройки, но пока не включено по умолчанию. Подробности, точки интеграции и план: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Принципы

- **Программист на первом месте.** Каждое решение проверяется вопросом: стало ли удобнее тому, кто пишет код?
- **Работает везде.** Любое железо, любая видеокарта, офлайн-режим там, где это возможно.
- **ИИ встроен, а не прикручен.** Модели доступны через один общий интерфейс, и любой проект экосистемы может ими пользоваться.
- **Без привязки к одному поставщику.** Облачные модели, локальные модели и бесплатные шлюзы взаимозаменяемы.
- **Каждый проект самостоятелен.** Его можно поставить и использовать отдельно, а вместе с остальными он даёт больше.

## Дорожная карта

Коротко: подключить все приложения к общему ИИ-шлюзу, встроить Mind IDE и ITIS Browser в AIsktagOS, довести фишки в духе Apple (синхронизация папок, «Локатор», виджеты), затем перенести систему на ARM, планшеты и телефоны. Полный план: [docs/ROADMAP.md](docs/ROADMAP.md).

## Для участников и ИИ-агентов

Правила экосистемы, шаблон раздела для README и порядок добавления нового проекта: [docs/CONVENTIONS.md](docs/CONVENTIONS.md).

## Автор

**Тагир Искалиев** — автор и создатель MindTagSystem и всех проектов экосистемы.
GitHub: [@tagiriskaliev18-hash](https://github.com/tagiriskaliev18-hash)
