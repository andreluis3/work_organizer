"""
Painel "Floresta de foco": grid de árvores + estatísticas rápidas
(foco total, produtividade).
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import ForestViewData
from frontend.pyqt_ui.widgets.stat_card import StatCard

TREES_PER_ROW = 4


class DashboardForestWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(10)

        title = QLabel("Floresta de foco")
        title.setObjectName("dashboardSectionTitle")
        root.addWidget(title)

        self.message_label = QLabel("Plante sua primeira arvore.")
        self.message_label.setObjectName("forestMessage")
        self.message_label.setWordWrap(True)
        root.addWidget(self.message_label)

        self.forest_container = QWidget()
        self.forest_grid = QGridLayout(self.forest_container)
        self.forest_grid.setSpacing(6)
        root.addWidget(self.forest_container)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        self.total_focus_card = StatCard("Foco total", value="0 min")
        self.productivity_card = StatCard("Produtividade", value="0%")
        stats_row.addWidget(self.total_focus_card)
        stats_row.addWidget(self.productivity_card)
        root.addLayout(stats_row)

    def update_data(self, data: ForestViewData) -> None:
        self.message_label.setText(data.message)

        while self.forest_grid.count():
            item = self.forest_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not data.trees:
            empty = QLabel("Sem arvores por enquanto.")
            empty.setObjectName("forestEmptyHint")
            self.forest_grid.addWidget(empty, 0, 0)
        else:
            for index, tree in enumerate(data.trees):
                row = index // TREES_PER_ROW
                col = index % TREES_PER_ROW
                tree_card = QFrame()
                tree_card.setObjectName("treeCard")
                tree_layout = QVBoxLayout(tree_card)
                tree_layout.setContentsMargins(6, 6, 6, 6)
                tree_label = QLabel(tree)
                tree_label.setObjectName("treeEmoji")
                tree_layout.addWidget(tree_label)
                self.forest_grid.addWidget(tree_card, row, col)

        self.total_focus_card.set_value(data.total_focus_text)
        self.total_focus_card.set_subtitle(data.total_focus_subtitle)
        self.productivity_card.set_value(data.productivity_text)
        self.productivity_card.set_subtitle(data.productivity_subtitle)