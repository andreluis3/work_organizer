from __future__ import annotations

from collections.abc import Callable

from backend.notes_manager import NotesManager
from notes.markdown_parser import render_markdown
from notes.templates import get_template


class NotesController:
    def __init__(self, notes_manager: NotesManager | None = None) -> None:
        self.notes_manager = notes_manager or NotesManager()
        self.current_note_id: int | None = None
        self.current_note_title = ""
        self.current_note_content = ""

        self._on_notes_change: Callable[[list[tuple]], None] | None = None
        self._on_note_change: Callable[[dict], None] | None = None
        self._on_preview_change: Callable[[str], None] | None = None
        self._on_status_change: Callable[[str, str], None] | None = None

    def bind(
        self,
        *,
        on_notes_change: Callable[[list[tuple]], None],
        on_note_change: Callable[[dict], None],
        on_preview_change: Callable[[str], None],
        on_status_change: Callable[[str, str], None],
    ) -> None:
        self._on_notes_change = on_notes_change
        self._on_note_change = on_note_change
        self._on_preview_change = on_preview_change
        self._on_status_change = on_status_change

    def initialize(self) -> None:
        self.refresh_notes()
        if self.current_note_id is not None:
            self.load_note(self.current_note_id)
            return

        notes = self.notes_manager.listar_notas()
        if notes:
            self.load_note(notes[0][0])
        else:
            self._emit_empty_note()
            self._emit_preview("")

    def refresh_notes(self, search_term: str = "") -> list[tuple]:
        query = search_term.strip()
        if query:
            notes = self.notes_manager.buscar_notas(query)
        else:
            notes = self.notes_manager.listar_notas()
        if self._on_notes_change is not None:
            self._on_notes_change(notes)
        return notes

    def create_note(self, template_name: str | None = None) -> None:
        template_key = template_name if template_name and template_name != "blank" else None
        title_base = self._base_title_for_template(template_key)
        title = self._generate_unique_title(title_base)
        content = get_template(template_key) if template_key else ""

        note_id = self.notes_manager.criar_nota(title, content)
        if note_id is None:
            self._emit_status("warning", "Nao foi possivel criar a nota.")
            return

        self.current_note_id = note_id
        self.current_note_title = title
        self.current_note_content = content
        self.refresh_notes()
        self.load_note(note_id)
        self._emit_status("success", "Nota criada.")

    def load_note(self, note_id: int) -> None:
        note = self.notes_manager.carregar_nota(note_id)
        if not note:
            self.current_note_id = None
            self.current_note_title = ""
            self.current_note_content = ""
            self._emit_empty_note()
            self._emit_preview("")
            self._emit_status("warning", "Nota nao encontrada.")
            return

        titulo, conteudo = note
        self.current_note_id = note_id
        self.current_note_title = titulo or "Sem titulo"
        self.current_note_content = conteudo or ""
        self._emit_note(
            {
                "id": note_id,
                "title": self.current_note_title,
                "content": self.current_note_content,
            }
        )
        self._emit_preview(self.current_note_content)

    def save_note(self, title: str, content: str) -> bool:
        clean_title = title.strip() or "Nova Nota"
        clean_content = content.rstrip()

        if self.current_note_id is None:
            note_id = self.notes_manager.criar_nota(clean_title, clean_content)
            if note_id is None:
                self._emit_status("warning", "Ja existe uma nota com esse titulo.")
                return False
            self.current_note_id = note_id
        else:
            ok = self.notes_manager.atualizar_nota(self.current_note_id, clean_title, clean_content)
            if not ok:
                self._emit_status("warning", "Ja existe uma nota com esse titulo.")
                return False

        self.current_note_title = clean_title
        self.current_note_content = clean_content
        self.refresh_notes()
        self.load_note(self.current_note_id)
        self._emit_status("success", "Nota salva.")
        return True

    def delete_current_note(self) -> None:
        if self.current_note_id is None:
            self._emit_status("info", "Nenhuma nota selecionada.")
            return

        deleted_id = self.current_note_id
        self.notes_manager.deletar_nota(deleted_id)
        self.current_note_id = None
        self.current_note_title = ""
        self.current_note_content = ""

        notes = self.refresh_notes()
        if notes:
            self.load_note(notes[0][0])
        else:
            self._emit_empty_note()
            self._emit_preview("")
        self._emit_status("success", "Nota removida.")

    def update_preview(self, content: str) -> None:
        self.current_note_content = content
        self._emit_preview(content)

    def apply_template_preview(self, template_name: str) -> str:
        if not template_name or template_name == "blank":
            return ""
        template = get_template(template_name)
        self._emit_preview(template)
        return template

    def _generate_unique_title(self, base_title: str) -> str:
        existing_titles = {note[1] for note in self.notes_manager.listar_notas()}
        if base_title not in existing_titles:
            return base_title

        suffix = 2
        while f"{base_title} {suffix}" in existing_titles:
            suffix += 1
        return f"{base_title} {suffix}"

    def _base_title_for_template(self, template_name: str | None) -> str:
        mapping = {
            "estudo": "Nota de Estudo",
            "codigo": "Snippet de Codigo",
            "resumo": "Resumo",
        }
        return mapping.get(template_name or "", "Nova Nota")

    def _emit_note(self, note_data: dict) -> None:
        if self._on_note_change is not None:
            self._on_note_change(note_data)

    def _emit_empty_note(self) -> None:
        self._emit_note({"id": None, "title": "", "content": ""})

    def _emit_preview(self, content: str) -> None:
        if self._on_preview_change is not None:
            self._on_preview_change(render_markdown(content))

    def _emit_status(self, level: str, message: str) -> None:
        if self._on_status_change is not None:
            self._on_status_change(level, message)
