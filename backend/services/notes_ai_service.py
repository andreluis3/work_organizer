"""Migração de notes_ai.py: heurísticas de tags e detecção de eventos."""

from __future__ import annotations

KEYWORDS = {
    "python": "dev",
    "esp32": "iot",
    "prova": "faculdade",
    "sistemas operacionais": "faculdade",
}


class NotesAIService:
    def suggest_tags(self, text: str) -> list[str]:
        lowered = (text or "").lower()
        return sorted({tag for keyword, tag in KEYWORDS.items() if keyword in lowered})

    def detect_event(self, text: str) -> str | None:
        if "prova" in (text or "").lower():
            return "Evento detectado: possivel prova"
        return None