"""
Regra de negócio de Notes: título único (com auto-numeração em conflito),
timestamps. Migração de notes_manager.py, separando SQL (repository) de
regra (service).
"""

from __future__ import annotations

from backend.database.notes_repository import NotesRepository

DEFAULT_TITLE = "Nova Nota"


class NotesService:
    def __init__(self, repository: NotesRepository | None = None) -> None:
        self.repository = repository or NotesRepository()

    def list_notes(self, search_term: str = "") -> list[dict]:
        term = (search_term or "").strip()
        return self.repository.search_notes(term) if term else self.repository.list_notes()

    def get_note(self, note_id: int) -> dict | None:
        return self.repository.get_note(note_id)

    def create_note(self, title: str | None = None, content: str = "") -> dict | None:
        clean_title = self._unique_title(title or DEFAULT_TITLE)
        note_id = self.repository.insert_note(clean_title, content)
        return self.get_note(note_id)

    def save_note(self, note_id: int, title: str, content: str) -> dict | None:
        clean_title = str(title or "").strip() or DEFAULT_TITLE
        if self.repository.title_exists(clean_title, ignore_id=note_id):
            clean_title = self._unique_title(clean_title, ignore_id=note_id)
        self.repository.update_note(note_id, clean_title, content)
        return self.get_note(note_id)

    def delete_note(self, note_id: int) -> None:
        self.repository.delete_note(note_id)

    def set_pinned(self, note_id: int, pinned: bool) -> dict | None:
        self.repository.set_pinned(note_id, pinned)
        return self.get_note(note_id)

    def _unique_title(self, base_title: str, ignore_id: int | None = None) -> str:
        if not self.repository.title_exists(base_title, ignore_id=ignore_id):
            return base_title
        suffix = 2
        while True:
            candidate = f"{base_title} {suffix}"
            if not self.repository.title_exists(candidate, ignore_id=ignore_id):
                return candidate
            suffix += 1