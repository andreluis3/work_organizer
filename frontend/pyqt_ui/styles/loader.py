# frontend/pyqt_ui/styles/loader.py
"""
Carrega e concatena os arquivos .qss da pasta styles/, na ordem certa.
Para adicionar tema de uma feature nova, crie um novo .qss aqui e liste
o nome em STYLE_FILES — nunca mais mexa em main_window.py para isso.
"""

from __future__ import annotations

from pathlib import Path

STYLES_DIR = Path(__file__).resolve().parent

STYLE_FILES = [
    "base.qss",
    "sidebar.qss",
    "topbar.qss",
    "dashboard.qss",
    "tasks.qss",
    "agenda.qss",
    "dialogs.qss",
    "notes.qss",
]


def load_stylesheet() -> str:
    parts: list[str] = []
    for filename in STYLE_FILES:
        path = STYLES_DIR / filename
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)