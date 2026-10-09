# Проекты MindTagSystem

Подробное описание каждого проекта экосистемы: что он делает, как устроен, на чём написан и какую роль играет. Автор всех проектов — Тагир Искалиев ([@tagiriskaliev18-hash](https://github.com/tagiriskaliev18-hash)).

Состояние описано на 9 октября 2026 года.

---

## Платформа

### AIsktagOS

**Репозиторий:** [tagiriskaliev18-hash/AisktagOS](https://github.com/tagiriskaliev18-hash/AisktagOS)
**Роль:** операционная система экосистемы, фундамент, на котором работает всё остальное.

Linux-дистрибутив для разработчиков. Внешне похож на macOS (строка меню, док, аналоги Spotlight и Mission Control, «светофор» на окнах, стиль Frosted Glass), по устройству ближе к Linux Mint: стабильная LTS-основа, никаких snap, снимки системы перед каждым обновлением.

- **Основа:** Ubuntu 26.04 LTS (поддержка до 2031 года), ядро Linux 7.0, KDE Plasma 6.6 на Wayland.
- **Любая видеокарта:** три уровня запаса, от аппаратного ускорения до X11 с `vesa`/`fbdev`, фирменный драйвер NVIDIA ставится в один клик.
- **Установщик:** Calamares, пошаговый мастер как у Windows, установка рядом с Windows, Secure Boot без настройки.
- **Файловая система:** Btrfs и Timeshift, откат одной кнопкой.
- **Из коробки для программиста:** VS Code, Git, GitHub CLI, lazygit, Docker, Podman, Distrobox, Python, Node.js, rustup, GCC/Clang, CMake, Neovim, kitty, zsh, starship, fzf, ripgrep.
- **«Центр AIsktagOS»** (`aisktag-center.py`) ставит в один клик Java, Go, .NET, JetBrains IDE, Android Studio, **Ollama** и **Claude Code**, то есть всё, что нужно для ИИ-ядра экосистемы.
- **Сборка:** `build.sh` (debootstrap → пакеты → squashfs → ISO с BIOS, UEFI и Secure Boot), ISO собирается в GitHub Actions и публикуется в Releases. Тестовый стенд `tools/test-vm.py` на QEMU.

**Место в экосистеме:** единая среда, в которую со временем будут встроены Mind IDE, ITIS Browser и ИИ-шлюз, чтобы после установки системы вся экосистема была готова к работе.

---

## Инструменты разработчика

### Mind IDE

**Репозиторий:** [tagiriskaliev18-hash/Mind-IDE](https://github.com/tagiriskaliev18-hash/Mind-IDE) (создаётся)
**Роль:** собственная среда разработки экосистемы, центральное рабочее место программиста.

IDE, которую Тагир разрабатывает сам. Исходники сейчас переносятся с его компьютера в отдельный репозиторий; подробное описание появится здесь, как только репозиторий будет опубликован.

**Место в экосистеме:** главный инструмент программиста в MindTagSystem. Работает поверх AIsktagOS и пользуется ИИ-ядром: мостом агентов, общим шлюзом и локальной моделью.

### ITIS Browser

**Репозиторий:** [tagiriskaliev18-hash/ITIS-browser](https://github.com/tagiriskaliev18-hash/ITIS-browser)
**Роль:** браузер экосистемы со встроенным ИИ-агентом.

Десктопный браузер «ITIS — Intelligence Browser» на PyQt6 и QtWebEngine (движок Chromium).

- Вкладки, своя стартовая страница «ITIS Search» с фоновыми изображениями и видео, поиск через Brave Search.
- **Боковая панель ИИ-агента** в духе HeyClicky: агент получает содержимое страницы, отвечает на вопросы и управляет страницей командами `[CLICK: текст]`, `[SCROLL_DOWN]`, `[SCROLL_UP]`.
- Модели: основной провайдер — OpenAI-совместимый endpoint, запасной — бесплатный Pollinations.
- **Корпоративный монитор** (`CorporateMonitor`): блокировка выбранных доменов и журнал посещений.
- Стек: Python, PyQt6, requests. Точка входа: `main.py`.

**Место в экосистеме:** веб-окно программиста. Следующий шаг — брать модели из общего шлюза AI Duo вместо прямых обращений к провайдерам.

---

## ИИ-ядро

### AI Duo (multimodel-agent)

**Репозиторий:** [tagiriskaliev18-hash/multimodel-agent](https://github.com/tagiriskaliev18-hash/multimodel-agent)
**Роль:** единый ИИ-шлюз экосистемы.

FastAPI-сервер, который прячет за одним OpenAI-совместимым API (`/v1/chat/completions`, `/v1/models`) разных провайдеров.

- **Провайдеры:** OpenAI (GPT-4o, o1, o3-mini), Nous Hermes через OpenRouter или Ollama, Groq LPU, локальная Ollama, бесплатный Pollinations.
- **Адаптер Hermes:** переводит ChatML-рассуждения `<scratchpad>` и вызовы `<tool_call>` в стандартные `delta.reasoning` и `delta.tool_calls`.
- **Fallback:** если нет ключа или кончилась квота, запрос уходит к следующему провайдеру; без единого ключа работает через Pollinations и Ollama.
- **Интерфейсы:** AI Studio Chat (`/chat`), 3D Neural HUD (`/hud`), сервисный портал (`/`), `/healthz`.
- **Агенты и навыки:** реестр ролей (`architect`, `reviewer`, `developer`, `security_auditor`, `llmops`, `hermes_agent`) и навыков (код-ревью, аудит безопасности и архитектуры).
- Разворачивается одной командой `docker compose up -d` вместе с Ollama.

**Место в экосистеме:** точка, через которую любой проект получает доступ к любой модели. Любое приложение, которое умеет говорить с OpenAI API, подключается к нему сменой адреса.

### antigravity-claude-bridge

**Репозиторий:** [tagiriskaliev18-hash/antigravity-claude-bridge](https://github.com/tagiriskaliev18-hash/antigravity-claude-bridge)
**Роль:** мост между ИИ-агентами разработчика.

Набор MCP-серверов, правил и навыков, который заставляет Google Antigravity (Gemini) и Claude Code работать как одна команда.

- **`claude_bridge.py`** — MCP-сервер с инструментами `claude_review`, `claude_ask`, `claude_implement`: Antigravity поручает Claude Code ревью и реализацию.
- **`multillm_bridge.py`** — MCP-сервер `multillm_ask` и `multillm_review`: доступ к пулу моделей (DeepSeek, GPT, Qwen, GLM, Claude) с приоритетами.
- **Навыки:** `context_booster` (быстрая карта зависимостей) и `multillm-orchestrator` (какая модель для какой задачи, экономия токенов).
- **Оптимизации:** ленивое ревью, пакетная отправка правок, параллельные субагенты, лимит итераций, сжатие контекста.
- **Установка:** `scripts/install.ps1` и `scripts/setup_claude_pro_ecosystem.ps1` (плагины Claude Code и настройка одним скриптом).

**Место в экосистеме:** «нервная система» разработки. Именно через этот мост ИИ-агенты помогают строить остальные проекты.

### qwen14b-coder-dev

**Репозиторий:** [tagiriskaliev18-hash/qwen14b-coder-dev](https://github.com/tagiriskaliev18-hash/qwen14b-coder-dev)
**Роль:** локальная модель для программирования, работает без интернета.

- Qwen 2.5 Coder 14B Instruct в квантовании `Q3_K_M` (~7,3 ГБ), все 49 слоёв в видеопамяти, рассчитано на видеокарты от 8 ГБ (RTX 3070 и выше).
- `Modelfile` для Ollama с системным промптом инженера.
- Веб-чат (`index.html` + `server.py`) со стримингом и подсветкой кода на `http://127.0.0.1:8008`.
- Запуск в один клик: `setup_and_run.bat` (Windows) и `setup_and_run.sh` (Linux, macOS).

**Место в экосистеме:** офлайн-мозг. Работает в Ollama, а Ollama уже понимают и AIsktagOS (установка в один клик), и шлюз AI Duo (провайдер `ollama`).

---

## Приложения

### FileHub AI

**Репозиторий:** [tagiriskaliev18-hash/filehub-ai](https://github.com/tagiriskaliev18-hash/filehub-ai)
**Роль:** облачное хранилище файлов с ИИ-агентом для компаний.

- **Файловый менеджер:** папки, загрузка, корзина, версии, поиск, ссылки для обмена.
- **ИИ-агент:** правит DOCX, PPTX и XLSX по текстовой просьбе, создаёт новые документы и показывает diff до сохранения.
- **Сжатие до заданного размера** и **конвертация** изображений, аудио, видео, таблиц и офисных документов (с LibreOffice).
- **Админка:** пользователи, роли, квоты, журнал аудита.
- **Стек:** монорепозиторий TypeScript (npm workspaces): Express + Prisma + SQLite в `apps/api`, React + Vite + Tailwind в `apps/web`.
- **Модели:** Anthropic API или любой OpenAI-совместимый сервер через `LOCALAI_BASE_URL` и `LOCALAI_MODEL`; без ключа работает всё, кроме чата.
- Размещается на Render (`render.yaml`, `DEPLOY.md`).

### SortApp — анализатор логов доступа к сетевым папкам

**Репозиторий:** [tagiriskaliev18-hash/sortapp](https://github.com/tagiriskaliev18-hash/sortapp) (закрытый)
**Роль:** инструмент для системных администраторов.

- Разбирает журналы Synology WinFileService (файлы `.txt` и поток syslog) и строит отчёты Excel.
- Роли администратора и работника; ограничения работника выполняются на сервере.
- Пароли хранятся хэшем scrypt, защита от перебора.
- **Стек:** Node.js без фреймворков, ExcelJS; размещается на Render.

### ИИ Доктор (medical-ai-assistant)

**Репозиторий:** [tagiriskaliev18-hash/medical-ai-assistant](https://github.com/tagiriskaliev18-hash/medical-ai-assistant)
**Роль:** клинический ассистент врача приёмного покоя и терапевта на принципах доказательной медицины.

- **Офлайн-PWA:** Service Worker кэширует все базы, приложение работает в браузере и на телефоне без интернета; публикуется на GitHub Pages.
- **Калькуляторы без ИИ-галлюцинаций:** СКФ CKD-EPI 2021, CURB-65, CHA₂DS₂-VASc, шкала Глазго считаются кодом, а не моделью.
- Интерпретация экстренных анализов, справочник дозировок и проверка лекарственных взаимодействий, генератор протокола осмотра SOAP с кодами МКБ-10, триаж «красных флагов», рабочее место триажа приёмного отделения.
- **FastAPI-бэкенд (по желанию):** проксирует модели через `LLM_BASE_URL` и `LLM_MODEL` (любой OpenAI-совместимый endpoint, по умолчанию DeepSeek).

**Место в экосистеме:** пример того, как MindTagSystem выходит за пределы программирования: та же платформа и то же ИИ-ядро для профессионалов в других областях.
