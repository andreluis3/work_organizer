"""
Seção "Resumo do dia": mensagem dinâmica + 3 StatCards
(última sessão, última task, curso atual).
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import HeroViewData
from frontend.pyqt_ui.widgets.stat_card import StatCard


class DashboardHeroWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel("Resumo do dia")
        title.setObjectName("dashboardSectionTitle")
        root.addWidget(title)

        self.dynamic_message_label = QLabel("Seu progresso aparece aqui.")
        self.dynamic_message_label.setObjectName("dashboardDynamicMessage")
        root.addWidget(self.dynamic_message_label)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self.last_session_card = StatCard("Ultima sessao")
        self.last_task_card = StatCard("Ultima task")
        self.course_card = StatCard("Curso atual")

        cards_row.addWidget(self.last_session_card)
        cards_row.addWidget(self.last_task_card)
        cards_row.addWidget(self.course_card)

        root.addLayout(cards_row)

    def update_data(self, data: HeroViewData) -> None:
        self.dynamic_message_label.setText(data.dynamic_message)

        self.last_session_card.set_value(data.last_session_value)
        self.last_session_card.set_subtitle(data.last_session_subtitle)

        self.last_task_card.set_value(data.last_task_value)
        self.last_task_card.set_subtitle(data.last_task_subtitle)

        self.course_card.set_value(data.course_value)
        self.course_card.set_subtitle(data.course_subtitle)