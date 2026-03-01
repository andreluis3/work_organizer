from __future__ import annotations

from pathlib import Path

from PIL import Image
import customtkinter as ctk


ICON_DIR = Path(__file__).resolve().parent / "assets" / "icons"


def load_icon(name: str, size: int = 18) -> ctk.CTkImage | None:
    path = ICON_DIR / name
    if not path.exists():
        return None
    return ctk.CTkImage(Image.open(path), size=(size, size))
