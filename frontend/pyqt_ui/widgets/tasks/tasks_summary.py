# frontend/pyqt_ui/widgets/tasks/tasks_summary.py
"""
Hero de resumo da tela de Tasks: total, pendentes, pausadas, concluídas
e cursos em andamento — em destaque, no topo da página.

Widget burro: recebe TasksSummaryData pronto e apenas exibe.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from frontend.pyqt_ui.viewmodels.tasks_viewmodel import TasksSummaryData

# (chave do objectName, título, cor de destaque)
STAT_DEFINITIONS = [
    ("total", "Total de tasks", "#38BDF8"),
    ("pending", "Pendentes", "#2563EB"),
    ("paused", "Pausadas", "#CA8A04"),
    ("completed", "Concluidas", "#16A34A"),
    ("courses", "Cursos em andamento", "#00F5FF"),
]


class _HeroStat(QFrame):
    def __init__(self, title: str, accent_color: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("heroStat")
        self.setFixedHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(2)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("heroStatValue")
        self.value_label.setStyleSheet(f"color: {accent_color};")
        layout.addWidget(self.value_label)

        title_label = QLabel(title)
        title_label.setObjectName("heroStatTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addStretch(1)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class TasksSummaryWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tasksHero")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._stats: dict[str, _HeroStat] = {}
        for key, title, color in STAT_DEFINITIONS:
            stat = _HeroStat(title, color)
            root.addWidget(stat, stretch=1)
            self._stats[key] = stat

    def update_data(self, data: TasksSummaryData) -> None:
        self._stats["total"].set_value(data.total_label)
        self._stats["pending"].set_value(data.pending_label)
        self._stats["paused"].set_value(data.paused_label)
        self._stats["completed"].set_value(data.completed_label)
        self._stats["courses"].set_value(data.courses_in_progress_label)