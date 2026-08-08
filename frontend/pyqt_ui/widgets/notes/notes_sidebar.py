"""Sidebar de Notes: busca, "+ Nova", lista com pin. Sem animação de
collapse nesta fase — foco em funcionalidade primeiro."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from frontend.pyqt_ui.viewmodels.notes_viewmodel import NoteListItem


class _NoteRow(QFrame):
    selected = pyqtSignal(int)
    pin_toggled = pyqtSignal(int, bool)

    def __init__(self, item: NoteListItem, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("noteRow")
        self.item = item
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        text_col = QVBoxLayout()
        title_label = QLabel(item.title)
        title_label.setObjectName("noteRowTitle")
        text_col.addWidget(title_label)

        date_label = QLabel(item.updated_label)
        date_label.setObjectName("noteRowDate")
        text_col.addWidget(date_label)

        layout.addLayout(text_col, stretch=1)

        self.pin_button = QPushButton("\u2605" if item.pinned else "\u2606")
        self.pin_button.setObjectName("pinButton")
        self.pin_button.setFixedWidth(28)
        self.pin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_button.clicked.connect(lambda: self.pin_toggled.emit(item.id, not item.pinned))
        layout.addWidget(self.pin_button)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.selected.emit(self.item.id)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class NotesSidebar(QFrame):
    search_changed = pyqtSignal(str)
    new_note_requested = pyqtSignal()
    note_selected = pyqtSignal(int)
    pin_toggled = pyqtSignal(int, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("notesSidebar")
        self.setFixedWidth(260)

        self._rows: dict[int, _NoteRow] = {}
        self._active_id: int | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("Notas")
        title.setObjectName("notesSidebarTitle")
        root.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Buscar notas...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        root.addWidget(self.search_input)

        new_button = QPushButton("+ Nova")
        new_button.setObjectName("primaryButton")
        new_button.clicked.connect(self.new_note_requested.emit)
        root.addWidget(new_button)

        scroll = QScrollArea()
        scroll.setObjectName("sectionScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch(1)

        scroll.setWidget(self._list_container)
        root.addWidget(scroll, stretch=1)

    def set_items(self, items: list[NoteListItem]) -> None:
        while self._list_layout.count() > 1:
            entry = self._list_layout.takeAt(0)
            if entry.widget():
                entry.widget().deleteLater()
        self._rows.clear()

        if not items:
            empty = QLabel("Nenhuma nota encontrada.")
            empty.setObjectName("sectionEmptyHint")
            self._list_layout.insertWidget(0, empty)
            return

        for index, item in enumerate(items):
            row = _NoteRow(item)
            row.selected.connect(self.note_selected.emit)
            row.pin_toggled.connect(self.pin_toggled.emit)
            row.set_active(item.id == self._active_id)
            self._list_layout.insertWidget(index, row)
            self._rows[item.id] = row

    def set_active_note(self, note_id: int | None) -> None:
        self._active_id = note_id
        for item_id, row in self._rows.items():
            row.set_active(item_id == note_id)