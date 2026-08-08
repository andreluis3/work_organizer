
from __future__ import annotations

from backend.services.notes_ai_service import NotesAIService
from backend.services.notes_service import NotesService


class NotesController:
    def __init__(self, service: NotesService | None = None, ai_service: NotesAIService | None = None) -> None:
        self.service = service or NotesService()
        self.ai_service = ai_service or NotesAIService()

    def list_notes(self, search_term: str = "") -> list[dict]:
        return self.service.list_notes(search_term)

    def get_note(self, note_id: int) -> dict | None:
        return self.service.get_note(note_id)

    def create_note(self) -> dict | None:
        return self.service.create_note()

    def save_note(self, note_id: int, title: str, content: str) -> dict | None:
        return self.service.save_note(note_id, title, content)

    def delete_note(self, note_id: int) -> None:
        self.service.delete_note(note_id)

    def toggle_pin(self, note_id: int, pinned: bool) -> dict | None:
        return self.service.set_pinned(note_id, pinned)

    def suggest_tags(self, text: str) -> list[str]:
        return self.ai_service.suggest_tags(text)

    def detect_event(self, text: str) -> str | None:
        return self.ai_service.detect_event(text)