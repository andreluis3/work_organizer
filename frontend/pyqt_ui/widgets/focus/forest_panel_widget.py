from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class ForestPanelWidget(QFrame):
    """Painel 'burro': mostra a floresta conquistada no mês."""

    COLUMNS = 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("forestPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        header = QLabel("ECOSSISTEMA")
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        self._message_label = QLabel("Plante sua primeira árvore.")
        self._message_label.setObjectName("forestMessage")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label)

        self._grid_container = QFrame()
        self._grid_container.setObjectName("forestGrid")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(8)
        layout.addWidget(self._grid_container)
        layout.addStretch(1)

    def update_data(self, forest_count: int, message: str) -> None:
        self._message_label.setText(message)
        self._render_forest(forest_count)

    def _render_forest(self, count: int) -> None:
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for index in range(count):
            row, column = divmod(index, self.COLUMNS)
            tree_label = QLabel("🌲")
            tree_label.setObjectName("treeIcon")
            tree_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid_layout.addWidget(tree_label, row, column)
