"""
ViewModel de Notes. Estado da lista, nota atual, busca e resultado das
heurísticas de IA. Nenhuma SQL, nenhum QWidget aqui.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from backend.controllers.notes_controller import NotesController


@dataclass(frozen=True, slots=True)
class NoteListItem:
    id: int
    title: str
    updated_label: str
    pinned: bool


@dataclass(frozen=True, slots=True)
class NoteContent:
    id: int | None
    title: str
    content: str


class NotesViewModel(QObject):
    notes_list_changed = pyqtSignal()
    note_loaded = pyqtSignal(object)  # NoteContent
    tags_changed = pyqtSignal(list)
    insight_changed = pyqtSignal(object)  # str | None
    status_changed = pyqtSignal(str, str)  # level, message

    def __init__(self, controller: NotesController | None = None) -> None:
        super().__init__()
        self.controller = controller or NotesController()
        self.notes: list[NoteListItem] = []
        self.current_note_id: int | None = None
        self.search_query = ""

    def initialize(self) -> None:
        self.refresh_notes()
        if self.notes:
            self.load_note(self.notes[0].id)
        else:
            self._emit_empty_note()

    def refresh_notes(self, search_term: str | None = None) -> None:
        if search_term is not None:
            self.search_query = search_term
        raw = self.controller.list_notes(self.search_query)
        self.notes = [self._build_item(item) for item in raw]
        self.notes_list_changed.emit()

    def create_note(self) -> None:
        note = self.controller.create_note()
        if not note:
            return
        self.refresh_notes()
        self.load_note(note["id"])
        self.status_changed.emit("success", "Nota criada")

    def load_note(self, note_id: int) -> None:
        note = self.controller.get_note(note_id)
        if not note:
            return
        self.current_note_id = note_id
        content = NoteContent(id=note_id, title=note.get("titulo", ""), content=note.get("conteudo", ""))
        self.note_loaded.emit(content)
        self.process_text(content.content)

    def save_note(self, title: str, content: str) -> None:
        if self.current_note_id is None:
            return
        updated = self.controller.save_note(self.current_note_id, title, content)
        if updated and updated.get("titulo") != title:
            # título ajustado por conflito de duplicata -> refletir na tela
            self.note_loaded.emit(NoteContent(id=self.current_note_id, title=updated["titulo"], content=content))
        self.refresh_notes()
        self.status_changed.emit("success", "Nota salva")

    def delete_current_note(self) -> None:
        if self.current_note_id is None:
            return
        self.controller.delete_note(self.current_note_id)
        self.current_note_id = None
        self.refresh_notes()
        self._emit_empty_note()
        self.status_changed.emit("info", "Nota excluida")

    def toggle_pin(self, note_id: int, pinned: bool) -> None:
        self.controller.toggle_pin(note_id, pinned)
        self.refresh_notes()

    def process_text(self, text: str) -> None:
        self.tags_changed.emit(self.controller.suggest_tags(text))
        self.insight_changed.emit(self.controller.detect_event(text))

    def _emit_empty_note(self) -> None:
        self.note_loaded.emit(NoteContent(id=None, title="", content=""))

    def _build_item(self, raw: dict) -> NoteListItem:
        updated = str(raw.get("data_atualizacao") or "")[:16].replace("T", " ")
        return NoteListItem(
            id=raw["id"],
            title=raw.get("titulo") or "Sem titulo",
            updated_label=updated or "Sem data",
            pinned=bool(raw.get("pinned")),
        )