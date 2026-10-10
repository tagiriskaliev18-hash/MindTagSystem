# MindKit — общие службы экосистемы MindTagSystem

MindKit — это то, что делает отдельные проекты экосистемой: связка ключей, связь между своими устройствами (общий буфер, Handoff, MindDrop), уведомления, поиск по всему, быстрые команды, ассистент Mind, каталог приложений и единый дизайн. Аналог системных фреймворков Apple. Какие фишки Apple он повторяет, смотрите в [APPLE.md](APPLE.md).

Только стандартная библиотека Python 3.10+, работает на Windows, Linux и macOS. В AIsktagOS MindKit уже встроен.

## Установка

```bash
pip install "mindkit[full] @ git+https://github.com/tagiriskaliev18-hash/MindTagSystem"
mindkit status
```

`[full]` добавляет `cryptography` (шифрование MindLink) и `keyring` (ключи в системном хранилище: Диспетчер учётных данных Windows, KWallet, Связка ключей macOS). Без них MindKit тоже работает: ключи лежат в файле, доступном только владельцу, а трафик подписан, но не зашифрован; `mindkit status` об этом пишет.

## Связка ключей

```bash
mindkit keychain set GROQ_API_KEY          # значение спросит без показа на экране
mindkit keychain import ~/projects/x/.env  # перенести все *_KEY, *_TOKEN, *_SECRET
mindkit keychain list                      # имена и первые/последние символы
eval "$(mindkit keychain env)"             # ключи в переменные окружения оболочки
```

В коде любого проекта:

```python
try:
    from mindkit import keychain
    keychain.load_env(["GROQ_API_KEY", "OPENAI_API_KEY"])  # уже заданные переменные не трогает
except ImportError:
    pass
```

Так уже сделано в Mind IDE (`aisktag_ai.py`) и шлюзе AI Duo (`server/app/config.py`).

## Мои устройства: MindLink

```bash
# на первом устройстве
mindkit link init            # печатает ключ аккаунта, храните его как пароль
mindkit link autostart on    # служба MindLink при входе в систему (Windows, Linux)
# на каждом следующем
mindkit link join XXXX-XXXX-…
mindkit link autostart on
mindkit link devices --scan  # найти свои устройства в сети
```

Если сеть не пропускает широковещательные пакеты (гостевой Wi-Fi, VPN), устройство добавляется по адресу: `mindkit link add 192.168.1.20`.

| Что | Команда |
|---|---|
| Общий буфер обмена | служба сама отправляет скопированный текст на все устройства; вручную: `mindkit copy текст` или `echo текст \| mindkit copy` |
| Handoff ссылки | `mindkit handoff url https://… [--to Ноутбук]` |
| Handoff файла со строкой | `mindkit handoff file src/main.py --line 42` (файлы до 4 МБ едут вместе с Handoff) |
| Продолжить | `mindkit handoff list`, `mindkit handoff resume [номер]` |
| MindDrop | `mindkit drop фото.png отчёт.pdf [--to Ноутбук]` → `~/Downloads/MindDrop` |
| Уведомление на все устройства | `mindkit notify "Сборка" "ISO готов" --devices` |
| История уведомлений | `mindkit notifications` |

Порты: 47800/TCP (запросы) и 47801/UDP (поиск устройств). Меняются через `mindkit config set link.port …`.

**Безопасность.** Ключ аккаунта — 256 бит, хранится в связке ключей. Каждый запрос подписан HMAC-SHA256 с меткой времени и одноразовым номером (повтор отклоняется), ответ тоже подписан, поэтому подставное устройство, подслушавшее поиск в сети, в список не попадёт. Содержимое шифруется AES-GCM, если установлен `cryptography`.

## Mind Search

```bash
mindkit search mind ide          # приложения, команды, настройки, имена ключей, Handoff, файлы
mindkit search pick_model --content --root ~/projects
```

Папки поиска: `search.roots` в настройках. В AIsktagOS тот же поиск встроен в KRunner (Meta+Space).

## Ассистент Mind

```bash
mindkit ask "чем отличается rebase от merge?"
git diff | mindkit ask "напиши сообщение коммита"
```

Сначала шлюз AI Duo (`gateway.url`, по умолчанию `http://127.0.0.1:8000/v1`), затем локальная Ollama (`ollama.url`). Ключ шлюза, если он нужен, берётся из связки ключей (`AIDUO_API_KEY`).

## Быстрые команды

```bash
mindkit shortcuts list
mindkit shortcuts run "Объяснить код"      # код из буфера → Mind → ответ в буфер и уведомление
mindkit shortcuts add моя-команда.json
```

Встроены: «Объяснить код», «Перевести буфер», «Буфер на устройства», «Запустить ИИ-ядро», «Commit-сообщение». Своя команда — JSON-файл:

```json
{
  "name": "Ревью diff",
  "description": "Mind смотрит staged-изменения и шлёт итог на все устройства",
  "steps": [
    {"action": "shell", "command": "git diff --staged"},
    {"action": "ask", "prompt": "Найди ошибки в этом diff:\n{{prev}}", "save": "review"},
    {"action": "clipboard.set"},
    {"action": "notify.devices", "title": "Ревью готово", "body": "{{review}}"}
  ]
}
```

Шаги: `clipboard.get`, `clipboard.set`, `text`, `ask`, `notify`, `notify.devices`, `shell`, `open`, `handoff`, `send_clipboard`, `app.run`, `shortcut`. Переменные: `{{prev}}` (результат прошлого шага), `{{input}}`, `{{device}}` и любые сохранённые через `"save"`.

## Mind Store

```bash
mindkit store list               # ✓ установлено, + можно поставить
mindkit store install mind-ide   # git clone в ~/MindTagSystem и установка зависимостей
mindkit store run mind-ide
mindkit store update             # git pull во всех установленных
```

Каталог — [`ecosystem.json`](../ecosystem.json): у каждого проекта раздел `app` с полями `kind`, `platforms`, `requires`, `install`, `run`. Новый проект попадает в Mind Store, как только его добавили в реестр.

## Дизайн Aurora

```bash
mindkit design build static/mind-ui   # mind-ui.css/.js/.qss, спрайт и SVG-иконки Mind
mindkit design css > aurora.css       # CSS: переменные --mt-*, градиент, 3D, bounce, иконки .mi-*
mindkit design qss > aurora.qss       # стиль Qt для настольных программ
mindkit design icon send              # одна иконка Mind в SVG
```

Правило единого стиля (без эмодзи, иконки Mind, переливающийся фиолетово-синий градиент, 3D, bounce) — в [DESIGN.md](DESIGN.md). Для PyQt6 — модуль `mindkit.qtfx` (иконки, пружина, перелив).

Источник правды — [`mindkit/data/tokens.json`](../mindkit/data/tokens.json). Те же токены лежат в Mind IDE (`overlay/usr/share/aisktagos/design/tokens.json`).

## Настройки

```bash
mindkit config list
mindkit config set device.name "Рабочий ПК"
mindkit config set gateway.url http://192.168.1.10:8000/v1
```

Файл: `~/.config/mindtagsystem/settings.json` (Windows: `%APPDATA%\MindTagSystem\settings.json`). Любую настройку перекрывает переменная окружения: `gateway.url` → `MINDTAG_GATEWAY_URL`.

## Разработка

```bash
python3 -m unittest discover -s tests -v   # 24 теста: два устройства, подписи, шифрование, поиск, команды
```

Тесты запускаются в GitHub Actions на Linux и Windows, с `cryptography`/`keyring` и без них.
