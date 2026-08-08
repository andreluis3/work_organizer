# frontend/pyqt_ui/widgets/tasks/kanban_column.py
"""
Coluna Kanban: cabeçalho com contador + lista de cards indexados por id.

Reutilizada para Pendente / Pausada / Concluída. Não conhece TaskCard
especificamente — só organiza QWidgets. A busca por título filtra
(esconde/mostra) os widgets já carregados, sem nova consulta ao banco.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class KanbanColumn(QFrame):
    def __init__(self, title: str, empty_text: str = "Nada por aqui ainda.", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("kanbanColumn")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        header_row = QHBoxLayout()
        header_label = QLabel(title)
        header_label.setObjectName("kanbanColumnHeader")
        header_row.addWidget(header_label)
        header_row.addStretch(1)

        self.count_label = QLabel("0")
        self.count_label.setObjectName("kanbanColumnCount")
        header_row.addWidget(self.count_label)
        root.addLayout(header_row)

        self._empty_text = empty_text
        self._items: dict[int, QWidget] = {}
        self._titles: dict[int, str] = {}

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
        root.addWidget(scroll, stretch=1)

        self._empty_label: QLabel | None = None
        self._refresh_empty_state()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def clear(self) -> None:
        for item_id in list(self._items.keys()):
            self.remove(item_id)

    def set_items(self, items: list[tuple[int, str, QWidget]]) -> None:
        """items: (id, título_para_busca, widget). Substituição completa."""
        self.clear()
        for item_id, title, widget in items:
            self.add(item_id, title, widget)

    def add(self, item_id: int, title: str, widget: QWidget) -> None:
        if item_id in self._items:
            self.remove(item_id)

        self._list_layout.insertWidget(self._list_layout.count() - 1, widget)
        self._items[item_id] = widget
        self._titles[item_id] = title.lower()
        self._update_count()
        self._refresh_empty_state()

    def remove(self, item_id: int) -> QWidget | None:
        widget = self._items.pop(item_id, None)
        self._titles.pop(item_id, None)
        if widget is not None:
            self._list_layout.removeWidget(widget)
            widget.deleteLater()
        self._update_count()
        self._refresh_empty_state()
        return widget

    def get(self, item_id: int) -> QWidget | None:
        return self._items.get(item_id)

    def filter_by_title(self, query: str) -> None:
        query = query.strip().lower()
        visible_count = 0
        for item_id, widget in self._items.items():
            matches = not query or query in self._titles.get(item_id, "")
            widget.setVisible(matches)
            if matches:
                visible_count += 1
        self.count_label.setText(str(visible_count))

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _update_count(self) -> None:
        self.count_label.setText(str(len(self._items)))

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