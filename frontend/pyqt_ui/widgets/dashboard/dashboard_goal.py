"""
Card de meta diária: sessões concluídas hoje vs meta configurada.

A cor (verde -> ciano ao completar) é decidida via propriedade dinâmica
de QSS ("completed"), não por lógica Python de cor — isso é 100%
responsabilidade visual do tema.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import GoalViewData


class DashboardGoalWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(8)

        header_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title = QLabel("Meta diaria")
        title.setObjectName("dashboardSectionTitle")
        title_col.addWidget(title)

        self.goal_label = QLabel("0/5 sessoes")
        self.goal_label.setObjectName("goalLabel")
        title_col.addWidget(self.goal_label)

        header_row.addLayout(title_col, stretch=1)

        self.goal_percent_label = QLabel("0%")
        self.goal_percent_label.setObjectName("goalPercent")
        header_row.addWidget(self.goal_percent_label)

        root.addLayout(header_row)

        self.goal_bar = QProgressBar()
        self.goal_bar.setObjectName("goalBar")
        self.goal_bar.setRange(0, 100)
        self.goal_bar.setTextVisible(False)
        self.goal_bar.setFixedHeight(14)
        root.addWidget(self.goal_bar)

        self.goal_hint_label = QLabel("Cada sessao concluida empurra sua meta para frente.")
        self.goal_hint_label.setObjectName("goalHint")
        self.goal_hint_label.setWordWrap(True)
        root.addWidget(self.goal_hint_label)

    def update_data(self, data: GoalViewData) -> None:
        self.goal_label.setText(data.goal_label)
        self.goal_percent_label.setText(data.goal_percent_text)
        self.goal_bar.setValue(int(data.goal_progress * 100))
        self.goal_hint_label.setText(data.goal_hint)

        state = "true" if data.is_completed else "false"
        self.goal_bar.setProperty("completed", state)
        self.goal_percent_label.setProperty("completed", state)
        self._refresh_style(self.goal_bar)
        self._refresh_style(self.goal_percent_label)

    @staticmethod
    def _refresh_style(widget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)