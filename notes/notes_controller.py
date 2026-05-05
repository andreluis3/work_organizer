from __future__ import annotations

from collections.abc import Callable

from backend.notes_manager import NotesManager
from notes.templates import get_template
from notes.notes_ai import sugerir_tags, detectar_evento


class NotesController:
    def __init__(self, notes_manager: NotesManager | None = None) -> None:
        self.notes_manager = notes_manager or NotesManager()

        self.current_note_id: int | None = None
        self.current_note_title = ""
        self.current_note_content = ""

        # callbacks UI
        self._on_notes_change = None
        self._on_note_change = None
        self._on_preview_change = None
        self._on_status_change = None
        self._on_tags_change = None
        self._on_insight_change = None

    def bind(
        self,
        *,
        on_notes_change,
        on_note_change,
        on_preview_change,
        on_status_change,
        on_tags_change,
        on_insight_change,
    ):
        self._on_notes_change = on_notes_change
        self._on_note_change = on_note_change
        self._on_preview_change = on_preview_change
        self._on_status_change = on_status_change
        self._on_tags_change = on_tags_change
        self._on_insight_change = on_insight_change

    def initialize(self):
        self.refresh_notes()

        notes = self.notes_manager.listar_notas()
        if notes:
            self.load_note(notes[0][0])
        else:
            self._emit_empty_note()

    # =========================
    # CRUD
    # =========================

    def refresh_notes(self, search_term: str = ""):
        notes = (
            self.notes_manager.buscar_notas(search_term)
            if search_term.strip()
            else self.notes_manager.listar_notas()
        )

        if self._on_notes_change:
            self._on_notes_change(notes)

    def create_note(self, template_name=None):
        content = get_template(template_name) if template_name else ""
        title = "Nova Nota"

        note_id = self.notes_manager.criar_nota(title, content)

        if note_id:
            self.load_note(note_id)
            self.refresh_notes()
            self._emit_status("success", "Nota criada")

    def load_note(self, note_id: int):
        note = self.notes_manager.carregar_nota(note_id)

        if not note:
            return

        titulo, conteudo = note

        self.current_note_id = note_id
        self.current_note_title = titulo
        self.current_note_content = conteudo

        if self._on_note_change:
            self._on_note_change({
                "id": note_id,
                "title": titulo,
                "content": conteudo,
            })

        self.process_text(conteudo)

    def save_note(self, title: str, content: str):
        if self.current_note_id is None:
            return

        self.notes_manager.atualizar_nota(
            self.current_note_id,
            title,
            content
        )

        self.refresh_notes()
        self._emit_status("success", "Nota salva")

    def delete_current_note(self):
        if not self.current_note_id:
            return

        self.notes_manager.deletar_nota(self.current_note_id)
        self.current_note_id = None

        self.refresh_notes()
        self._emit_empty_note()

    # =========================
    # IA (CORE NOVO)
    # =========================

    def process_text(self, texto: str):
        tags = sugerir_tags(texto)
        insight = detectar_evento(texto)

        if self._on_tags_change:
            self._on_tags_change(tags)

        if self._on_insight_change:
            self._on_insight_change(insight)

        if self._on_preview_change:
            self._on_preview_change(texto)  # preview simples por enquanto

    # =========================
    # UI EMIT
    # =========================

    def _emit_empty_note(self):
        if self._on_note_change:
            self._on_note_change({"id": None, "title": "", "content": ""})

    def _emit_status(self, level, msg):
        if self._on_status_change:
            self._on_status_change(level, msg)