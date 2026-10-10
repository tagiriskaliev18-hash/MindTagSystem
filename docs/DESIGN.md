# Единый стиль Mind

Правило Тагира для **всех** интерфейсов экосистемы: сайтов, веб-интерфейсов, настольных программ, ОС, презентаций.

1. **Никаких эмодзи в интерфейсе.** Кнопки, меню, вкладки, значки и уведомления используют только иконки Mind.
2. **Иконки Mind** — свои рисунки (24×24, обводка 2px, скруглённые концы), залитые фиолетово-синим градиентом.
3. **Фиолетово-синий градиент переливается**: `#a46cf0 → #7c66df → #5b8dee → #49b3f7`, медленно течёт по кругу (6 с).
4. **3D-вставки**: объёмные кнопки (блик сверху, тень снизу, многослойная тень), карточки с глубиной и наклоном за курсором, шар-«орб» Mind.
5. **Bounce**: пружина при наведении, нажатии и появлении (`cubic-bezier(0.34, 1.56, 0.64, 1)`).
6. Тёмная тема Aurora по умолчанию; при `prefers-reduced-motion` анимации выключаются.

Источник правды — MindKit: [`mindkit/data/tokens.json`](../mindkit/data/tokens.json) (цвета, градиент, движение, глубина) и [`mindkit/data/icons.json`](../mindkit/data/icons.json) (иконки). Витрина всех иконок и эффектов — [`design/index.html`](../design/index.html).

## Как подключить

### Веб (любой проект)

Скопируйте папку [`design/`](../design) к себе (или соберите её: `mindkit design build static/mind-ui`) и подключите:

```html
<link rel="stylesheet" href="mind-ui.css">
<script src="mind-ui.js" defer></script>

<button class="mt-btn"><i class="mi mi-send"></i>Отправить</button>
<button class="mt-btn mt-btn-ghost"><i class="mi mi-sparkles"></i>Спросить Mind</button>
<button class="mt-icon-btn" title="Поиск"><i class="mi mi-search"></i></button>
<div class="mt-card mt-3d" data-mt-tilt>…</div>
<h1 class="mt-gradient-text">MindMail</h1>
```

| Класс | Что делает |
|---|---|
| `mi mi-<имя>` | иконка Mind с живым градиентом (`mi-mono` — цветом текста, `mi-white` — белая) |
| `mt-btn`, `mt-btn-ghost`, `mt-icon-btn` | объёмные кнопки с переливом и пружиной |
| `mt-gradient`, `mt-gradient-text`, `mt-gradient-border` | переливающийся фон, текст, рамка |
| `mt-card`, `mt-3d` + `data-mt-tilt` | карточка с глубиной, наклон за курсором |
| `mt-orb` | объёмный шар Mind (аватар ИИ, индикатор) |
| `mt-bounce`, `mt-bounce-in`, `mt-bouncing` | пружина при наведении, при появлении, разовый прыжок |

Из JavaScript: `MindUI.icon('inbox')` вернёт готовый `<i class="mi mi-inbox">`. В React — `<i className="mi mi-inbox" />`.

Проекты, у которых свой CSS, берут переменные `--mt-gradient-flow`, `--mt-spring`, `--mt-depth-raised`, `--mt-depth-highlight` и т. д.

### Qt (PyQt6)

```python
from mindkit import qtfx
app.setStyleSheet(qtfx.stylesheet())   # градиентные объёмные кнопки
btn.setIcon(qtfx.icon("send"))         # иконка Mind с градиентом
qtfx.bounce_on_hover(btn)              # пружина
qtfx.shimmer(header)                   # переливающийся градиент
```

Без MindKit: `design/mind-ui.qss` и SVG-иконки `design/icons/*.svg` (градиент уже внутри).

### Команды

```bash
mindkit design css | qss | js | sprite | json
mindkit design icons            # список имён
mindkit design icon send        # одна иконка SVG
mindkit design build <папка>    # все файлы для проекта
```

## Новая иконка

Добавьте её в `mindkit/data/icons.json` (только `<path>`/`<circle>`/`<rect>`, без заливки и цвета — градиент ставит тема), затем `python3 -m mindkit design build design` и скопируйте `design/` в проекты.
