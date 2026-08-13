from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class _MetricCard(QFrame):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("metricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        title_label = QLabel(title.upper())
        title_label.setObjectName("metricTitle")
        layout.addWidget(title_label)

        self._value_label = QLabel("--")
        self._value_label.setObjectName("metricValue")
        layout.addWidget(self._value_label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)


class MetricsPanelWidget(QFrame):
    """Painel 'burro': recebe DTO pronto e só atualiza os cards/chip."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("metricsPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header = QLabel("MÉTRICAS")
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        self._total_focused_card = _MetricCard("Tempo total focado")
        self._sessions_card = _MetricCard("Sessões completas")
        layout.addWidget(self._total_focused_card)
        layout.addWidget(self._sessions_card)

        self._status_chip = QLabel("SISTEMA PRONTO")
        self._status_chip.setObjectName("statusChip")
        layout.addWidget(self._status_chip)
        layout.addStretch(1)

    def update_data(self, total_focused: str, completed_sessions: str, is_running: bool) -> None:
        self._total_focused_card.set_value(total_focused)
        self._sessions_card.set_value(completed_sessions)

        self._status_chip.setText("EM EXECUÇÃO" if is_running else "SISTEMA PRONTO")
        self._status_chip.setProperty("running", is_running)
        self._status_chip.style().unpolish(self._status_chip)
        self._status_chip.style().polish(self._status_chip)
