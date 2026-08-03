# frontend/pyqt_ui/widgets/topbar.py
"""
Barra superior da nova interface PyQt6.

Exibe o título (e opcionalmente subtítulo) da página atual. Reserva uma
área à direita (`actions_layout`) para componentes futuros (busca,
notificações), sem precisar mexer na estrutura quando isso chegar.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel, QVBoxLayout


class TopBar(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(8)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(0)

        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("topbarTitle")
        title_column.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("topbarSubtitle")
        self.subtitle_label.setVisible(False)
        title_column.addWidget(self.subtitle_label)

        layout.addLayout(title_column)
        layout.addStretch(1)

        # Área reservada para ações futuras (busca, notificações, avatar...)
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        layout.addLayout(self.actions_layout)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))
        