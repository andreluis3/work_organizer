"""
Card de um dia no grid mensal da agenda.

Puramente visual: recebe os eventos já filtrados e apenas os exibe.
Não conhece AgendaManager nem abre diálogos — só emite `clicked(date)`.
"""

from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from core.agenda_manager import Event


class CalendarDayCell(QFrame):
    clicked = pyqtSignal(date)

    MAX_VISIBLE_EVENTS = 3

    def __init__(self, day: date, in_month: bool, is_today: bool, parent=None) -> None:
        super().__init__(parent)
        self.day = day

        if is_today:
            self.setObjectName("dayCellToday")
        elif in_month:
            self.setObjectName("dayCell")
        else:
            self.setObjectName("dayCellOutside")

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(90)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)
        self._layout.setSpacing(3)

        day_label = QLabel(str(day.day))
        day_label.setObjectName("dayCellNumber" if in_month else "dayCellNumberOutside")
        self._layout.addWidget(day_label)
        self._layout.addStretch(1)

    def set_events(self, events: list[Event]) -> None:
        # Mantém apenas o número do dia (índice 0) e o stretch (último); remove pílulas antigas.
        while self._layout.count() > 2:
            item = self._layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        visible = events[: self.MAX_VISIBLE_EVENTS]
        for index, event in enumerate(visible):
            pill = QLabel(self._truncate(event.title))
            pill.setObjectName("eventPill")
            pill.setStyleSheet(f"background-color: {event.color}; color: #0B0F16;")
            self._layout.insertWidget(1 + index, pill)

        remaining = len(events) - len(visible)
        if remaining > 0:
            more_label = QLabel(f"+{remaining} eventos")
            more_label.setObjectName("dayCellMore")
            self._layout.insertWidget(1 + len(visible), more_label)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - nome exigido pelo Qt
        super().mouseReleaseEvent(event)
        self.clicked.emit(self.day)

    @staticmethod
    def _truncate(title: str, limit: int = 16) -> str:
        clean = str(title or "Evento").strip()
        return clean if len(clean) <= limit else f"{clean[: limit - 1]}…"