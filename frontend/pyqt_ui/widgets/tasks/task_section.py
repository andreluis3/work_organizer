# frontend/pyqt_ui/widgets/tasks/task_section.py
"""
Container genérico de itens, indexado por id, com estado vazio.

Reutilizado para "Em andamento", "Concluídas" e "Cursos em andamento".
Não sabe o que é um TaskCard ou CourseCard — só organiza QWidgets por id
dentro de uma QVBoxLayout com scroll. Quem cria os cards e conecta sinais
é a TasksPage; esta classe só posiciona/remove.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class TaskSection(QWidget):
    def __init__(self, title: str, empty_text: str = "Nada por aqui ainda.", parent=None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QLabel(title)
        header.setObjectName("sectionHeader")
        root.addWidget(header)

        self._empty_text = empty_text
        self._items: dict[int, QWidget] = {}

        scroll = QScrollArea()
        scroll.setObjectName("sectionScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch(1)

        scroll.setWidget(self._list_container)
        root.addWidget(scroll)

        self._empty_label: QLabel | None = None
        self._refresh_empty_state()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def clear(self) -> None:
        for item_id in list(self._items.keys()):
            self.remove(item_id)

    def set_items(self, items: list[tuple[int, QWidget]]) -> None:
        """Substituição completa (usada só em refresh() de carga inicial)."""
        self.clear()
        for item_id, widget in items:
            self.add(item_id, widget)

    def add(self, item_id: int, widget: QWidget) -> None:
        if item_id in self._items:
            self.remove(item_id)

        # insere antes do stretch final
        self._list_layout.insertWidget(self._list_layout.count() - 1, widget)
        self._items[item_id] = widget
        self._refresh_empty_state()

    def remove(self, item_id: int) -> QWidget | None:
        widget = self._items.pop(item_id, None)
        if widget is not None:
            self._list_layout.removeWidget(widget)
            widget.deleteLater()
        self._refresh_empty_state()
        return widget

    def get(self, item_id: int) -> QWidget | None:
        return self._items.get(item_id)

    def has(self, item_id: int) -> bool:
        return item_id in self._items

    # ------------------------------------------------------------------
    # Estado vazio
    # ------------------------------------------------------------------

    def _refresh_empty_state(self) -> None:
        is_empty = len(self._items) == 0

        if is_empty and self._empty_label is None:
            self._empty_label = QLabel(self._empty_text)
            self._empty_label.setObjectName("sectionEmptyHint")
            self._list_layout.insertWidget(0, self._empty_label)
        elif not is_empty and self._empty_label is not None:
            self._list_layout.removeWidget(self._empty_label)
            self._empty_label.deleteLater()
            self._empty_label = None