"""Página de Notes: sidebar + editor. Sem painel de preview separado
(Fase 1) — o highlighting do NotesEditor já entrega leitura próxima de
WYSIWYG."""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.viewmodels.notes_viewmodel import NoteContent, NotesViewModel
from frontend.pyqt_ui.widgets.notes.notes_editor import NotesEditor
from frontend.pyqt_ui.widgets.notes.notes_sidebar import NotesSidebar


class NotesPage(BasePage):
    title = "Notas"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.viewmodel = NotesViewModel()
        self.viewmodel.notes_list_changed.connect(self._on_notes_list_changed)
        self.viewmodel.note_loaded.connect(self._on_note_loaded)
        self.viewmodel.tags_changed.connect(self._on_tags_changed)
        self.viewmodel.insight_changed.connect(self._on_insight_changed)
        self.viewmodel.status_changed.connect(self._on_status_changed)

        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)

        self.sidebar = NotesSidebar()
        self.sidebar.search_changed.connect(self._on_search_changed)
        self.sidebar.new_note_requested.connect(self.viewmodel.create_note)
        self.sidebar.note_selected.connect(self.viewmodel.load_note)
        self.sidebar.pin_toggled.connect(self.viewmodel.toggle_pin)
        row.addWidget(self.sidebar)

        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(10)

        header_row = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setObjectName("noteTitleInput")
        self.title_input.setPlaceholderText("Titulo da nota")
        header_row.addWidget(self.title_input, stretch=1)

        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self._save_note)
        header_row.addWidget(save_button)

        delete_button = QPushButton("Excluir")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.viewmodel.delete_current_note)
        header_row.addWidget(delete_button)

        editor_layout.addLayout(header_row)

        self.editor = NotesEditor()
        self.editor.content_changed.connect(self.viewmodel.process_text)
        editor_layout.addWidget(self.editor, stretch=1)

        self.tags_label = QLabel("Tags:")
        self.tags_label.setObjectName("notesTagsLabel")
        editor_layout.addWidget(self.tags_label)

        self.insight_label = QLabel("")
        self.insight_label.setObjectName("notesInsightLabel")
        self.insight_label.setWordWrap(True)
        editor_layout.addWidget(self.insight_label)

        self.status_label = QLabel("Pronto.")
        self.status_label.setObjectName("notesStatusLabel")
        editor_layout.addWidget(self.status_label)

        row.addWidget(editor_panel, stretch=1)

        container = QWidget()
        container.setLayout(row)
        self.add_content_widget(container)

    def on_show(self) -> None:
        super().on_show()
        self.viewmodel.initialize()

    def _on_notes_list_changed(self) -> None:
        self.sidebar.set_items(self.viewmodel.notes)
        self.sidebar.set_active_note(self.viewmodel.current_note_id)

    def _on_note_loaded(self, content: NoteContent) -> None:
        self.title_input.setText(content.title)
        self.editor.set_content(content.content)
        self.sidebar.set_active_note(content.id)

    def _on_tags_changed(self, tags: list[str]) -> None:
        text = ", ".join(tags)
        self.tags_label.setText(f"Tags: {text}" if text else "Tags:")

    def _on_insight_changed(self, insight) -> None:
        self.insight_label.setText(str(insight or ""))

    def _on_status_changed(self, level: str, message: str) -> None:
        colors = {"success": "#22C55E", "warning": "#F59E0B", "info": "#94A3B8"}
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {colors.get(level, '#94A3B8')};")

    def _on_search_changed(self, text: str) -> None:
        self.viewmodel.refresh_notes(text)

    def _save_note(self) -> None:
        self.viewmodel.save_note(self.title_input.text(), self.editor.get_content())