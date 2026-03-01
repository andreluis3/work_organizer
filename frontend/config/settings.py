from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppSettings:
    theme: str = "dark"
    accent: str = "blue"


class SettingsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or (Path(__file__).resolve().parent / "settings.json")

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()

        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            return AppSettings()

        return AppSettings(
            theme=data.get("theme", "dark"),
            accent=data.get("accent", "blue"),
        )

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theme": settings.theme,
            "accent": settings.accent,
        }
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=True, indent=2)
