"""
Cabeçalho do Dashboard: boas-vindas, barra de XP e painel de streak.

Widget burro: recebe um HeaderViewData já pronto do DashboardViewModel e
apenas atualiza labels/progress bar. Nenhum cálculo aqui.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import HeaderViewData


class DashboardHeaderWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(6)

        self.welcome_label = QLabel("Bem-vindo de volta")
        self.welcome_label.setObjectName("dashboardWelcome")
        left.addWidget(self.welcome_label)

        self.summary_label = QLabel("XP: 0 | Nivel 1 | 0 dias")
        self.summary_label.setObjectName("dashboardSummary")
        left.addWidget(self.summary_label)

        self.xp_bar = QProgressBar()
        self.xp_bar.setObjectName("xpBar")
        self.xp_bar.setRange(0, 100)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setFixedHeight(12)
        left.addWidget(self.xp_bar)

        self.xp_caption = QLabel("0/100 XP para o proximo nivel")
        self.xp_caption.setObjectName("xpCaption")
        left.addWidget(self.xp_caption)

        root.addLayout(left, stretch=1)

        streak_panel = QFrame()
        streak_panel.setObjectName("streakPanel")
        streak_layout = QVBoxLayout(streak_panel)
        streak_layout.setContentsMargins(16, 14, 16, 14)
        streak_layout.setSpacing(4)

        streak_title = QLabel("STREAK")
        streak_title.setObjectName("streakTitle")
        streak_layout.addWidget(streak_title)

        self.streak_value_label = QLabel("0 dias")
        self.streak_value_label.setObjectName("streakValue")
        streak_layout.addWidget(self.streak_value_label)

        self.streak_hint_label = QLabel("Mantenha o ritmo hoje.")
        self.streak_hint_label.setObjectName("streakHint")
        self.streak_hint_label.setWordWrap(True)
        streak_layout.addWidget(self.streak_hint_label)

        root.addWidget(streak_panel)

    def update_data(self, data: HeaderViewData) -> None:
        self.welcome_label.setText(data.welcome_text)
        self.summary_label.setText(data.summary_text)
        self.xp_bar.setValue(int(data.xp_progress * 100))
        self.xp_caption.setText(data.xp_caption)
        self.streak_value_label.setText(data.streak_value_text)
        self.streak_hint_label.setText(data.streak_hint_text)