# frontend/pyqt_ui/widgets/tasks/history_section.py
"""
Lista de histórico (tasks concluídas movidas para o histórico).

Somente leitura — recarrega por completo a cada refresh(), já que histórico
não sofre atualização granular (não é alvo de cliques na tela de Tasks).
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from frontend.pyqt_ui.viewmodels.tasks_viewmodel import HistoryItemData


class _HistoryRow(QFrame):
    def __init__(self, data: HistoryItemData, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("historyRow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        title_label = QLabel(data.title)
        title_label.setObjectName("historyRowTitle")
        layout.addWidget(title_label)

        date_label = QLabel(data.completed_at)
        date_label.setObjectName("historyRowDate")
        layout.addWidget(date_label)


class HistorySection(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QLabel("Historico")
        header.setObjectName("sectionHeader")
        root.addWidget(header)

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
        root.addWidget(scroll)

    def set_items(self, items: list[HistoryItemData]) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            empty = QLabel("Nenhum item no historico ainda.")
            empty.setObjectName("sectionEmptyHint")
            self._list_layout.insertWidget(0, empty)
            return

        for index, data in enumerate(items):
            row = _HistoryRow(data)
            self._list_layout.insertWidget(index, row)