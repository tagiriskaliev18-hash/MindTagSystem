#!/usr/bin/env python3
"""Печатает раздел «Часть экосистемы MindTagSystem» для README проекта.

Использование:
    python3 tools/readme-section.py <id проекта из ecosystem.json>

Источник данных — ecosystem.json в корне репозитория. Готовый раздел
вставляется в конец README проекта вместо старого.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def section(eco: dict, me: str) -> str:
    layers = {layer["id"]: layer["title"] for layer in eco["layers"]}
    projects = {p["id"]: p for p in eco["projects"]}
    if me not in projects:
        sys.exit(f"Нет проекта «{me}». Есть: {', '.join(projects)}")
    p = projects[me]
    author = eco["author"]
    rows = []
    for x in eco["projects"]:
        if x["id"] == me:
            name = f"**{x['name']}** ← вы здесь"
        else:
            name = f"[{x['name']}](https://github.com/{x['repo']})"
        rows.append(f"| {layers[x['layer']]} | {name} | {x['tagline']} |")
    role = p["role"][0].lower() + p["role"][1:]
    return "\n".join([
        "## 🌐 Часть экосистемы MindTagSystem",
        "",
        f"{p['name']} входит в **[MindTagSystem]({eco['hub']})** — экосистему для программистов, "
        f"которую создаёт **{author['name']}** ([@{author['github']}]({author['url']})): "
        "своя операционная система, браузер, IDE, ИИ-ядро и приложения, которые работают вместе "
        "и которые можно встроить в любое устройство.",
        "",
        f"**Роль в экосистеме:** {role} (слой «{layers[p['layer']]}»).",
        "",
        "| Слой | Проект | Что делает |",
        "|---|---|---|",
        *rows,
        "",
        f"Как проекты связаны между собой: [архитектура MindTagSystem]({eco['hub']}/blob/main/docs/ARCHITECTURE.md). "
        f"Автор всех проектов экосистемы — {author['name']}.",
    ])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    eco = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))
    print(section(eco, sys.argv[1]))
