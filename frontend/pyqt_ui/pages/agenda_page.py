"""
Página de Agenda: aba de calendário mensal + aba de planner semanal.

Migração do antigo frontend/telas/agenda.py (CustomTkinter). Mantém o
mesmo padrão do original: instancia AgendaManager diretamente (não existe
AgendaController hoje), pois os eventos vivem em memória, sem SQLite.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.agenda_manager import AgendaManager, Event
from frontend.pyqt_ui.dialogs.event_dialog import EventDialog
from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.widgets.calendar_day_cell import CalendarDayCell

WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


class _HourCell(QFrame):
    """Célula clicável do planner semanal. Só emite `clicked`, sem lógica."""

    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        super().mouseReleaseEvent(event)
        self.clicked.emit()


class AgendaPage(BasePage):
    title = "Agenda"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.agenda_manager = AgendaManager()
        self.today = datetime.now().date()
        self.month_cursor = self.today.replace(day=1)
        self.week_cursor = self.today

        self.tabs = QTabWidget()
        self.add_content_widget(self.tabs)

        self.calendar_tab = QWidget()
        self.week_tab = QWidget()
        self.tabs.addTab(self.calendar_tab, "Calendário")
        self.tabs.addTab(self.week_tab, "Planner Semanal")

        self._build_calendar_tab()
        self._build_week_tab()
        self._refresh_all()

    # ------------------------------------------------------------------
    # Aba: Calendário mensal
    # ------------------------------------------------------------------

    def _build_calendar_tab(self) -> None:
        layout = QVBoxLayout(self.calendar_tab)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)

        top = QHBoxLayout()
        prev_btn = QPushButton("<")
        prev_btn.setFixedWidth(36)
        prev_btn.clicked.connect(lambda: self._shift_month(-1))
        top.addWidget(prev_btn)

        self.month_label = QLabel("")
        self.month_label.setObjectName("agendaCursorLabel")
        top.addWidget(self.month_label, stretch=1)

        today_btn = QPushButton("Hoje")
        today_btn.setFixedWidth(62)
        today_btn.clicked.connect(self._go_today)
        top.addWidget(today_btn)

        next_btn = QPushButton(">")
        next_btn.setFixedWidth(36)
        next_btn.clicked.connect(lambda: self._shift_month(1))
        top.addWidget(next_btn)

        layout.addLayout(top)

        weekdays_row = QHBoxLayout()
        for day_name in WEEKDAYS:
            label = QLabel(day_name)
            label.setObjectName("agendaWeekdayHeader")
            weekdays_row.addWidget(label, stretch=1)
        layout.addLayout(weekdays_row)

        self.month_grid = QGridLayout()
        self.month_grid.setSpacing(4)
        for col in range(7):
            self.month_grid.setColumnStretch(col, 1)
        for row in range(6):
            self.month_grid.setRowStretch(row, 1)

        grid_container = QWidget()
        grid_container.setLayout(self.month_grid)
        layout.addWidget(grid_container, stretch=1)

    def _render_month_calendar(self) -> None:
        self.month_label.setText(self._capitalized_month(self.month_cursor))

        while self.month_grid.count():
            item = self.month_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cal = calendar.Calendar(firstweekday=0)
        matrix = list(cal.monthdatescalendar(self.month_cursor.year, self.month_cursor.month))
        while len(matrix) < 6:
            last_day = matrix[-1][-1]
            matrix.append([last_day + timedelta(days=i + 1) for i in range(7)])

        for row_idx, week in enumerate(matrix[:6]):
            for col_idx, day in enumerate(week):
                in_month = day.month == self.month_cursor.month
                is_today = day == self.today

                cell = CalendarDayCell(day, in_month=in_month, is_today=is_today)
                cell.set_events(self.agenda_manager.get_events_day(day))
                cell.clicked.connect(self._open_day_dialog)
                self.month_grid.addWidget(cell, row_idx, col_idx)

    # ------------------------------------------------------------------
    # Aba: Planner semanal
    # ------------------------------------------------------------------

    def _build_week_tab(self) -> None:
        layout = QVBoxLayout(self.week_tab)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)

        top = QHBoxLayout()
        prev_btn = QPushButton("<")
        prev_btn.setFixedWidth(36)
        prev_btn.clicked.connect(lambda: self._shift_week(-1))
        top.addWidget(prev_btn)

        self.week_label = QLabel("")
        self.week_label.setObjectName("agendaCursorLabel")
        top.addWidget(self.week_label, stretch=1)

        today_btn = QPushButton("Hoje")
        today_btn.setFixedWidth(62)
        today_btn.clicked.connect(self._go_today)
        top.addWidget(today_btn)

        next_btn = QPushButton(">")
        next_btn.setFixedWidth(36)
        next_btn.clicked.connect(lambda: self._shift_week(1))
        top.addWidget(next_btn)

        layout.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.week_grid_container = QWidget()
        self.week_grid = QGridLayout(self.week_grid_container)
        self.week_grid.setSpacing(4)

        scroll.setWidget(self.week_grid_container)
        layout.addWidget(scroll, stretch=1)

    def _render_week_planner(self) -> None:
        while self.week_grid.count():
            item = self.week_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        week_days = self.agenda_manager.week_days(self.week_cursor)
        week_start, week_end = week_days[0], week_days[-1]
        self.week_label.setText(
            f"Semana {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}"
        )

        self.week_grid.setColumnStretch(0, 0)
        for col in range(1, 8):
            self.week_grid.setColumnStretch(col, 1)

        hour_header = QLabel("Hora")
        hour_header.setObjectName("agendaWeekdayHeader")
        self.week_grid.addWidget(hour_header, 0, 0)

        for idx, day in enumerate(week_days, start=1):
            caption = f"{WEEKDAYS[idx - 1]}\n{day.strftime('%d/%m')}"
            head = QLabel(caption)
            head.setObjectName("agendaWeekdayHeader")
            self.week_grid.addWidget(head, 0, idx)

        events_week = self.agenda_manager.get_events_for_week(self.week_cursor)
        events_index: dict[tuple[date, int], list[Event]] = {}
        for event in events_week:
            key = (event.start.date(), event.start.hour)
            events_index.setdefault(key, []).append(event)

        for row_offset, hour in enumerate(range(8, 23), start=1):
            hour_label = QLabel(f"{hour:02d}:00")
            hour_label.setObjectName("agendaHourLabel")
            self.week_grid.addWidget(hour_label, row_offset, 0)

            for col, day in enumerate(week_days, start=1):
                cell_events = events_index.get((day, hour), [])
                cell = self._build_hour_cell(day, hour, cell_events)
                self.week_grid.addWidget(cell, row_offset, col)

    def _build_hour_cell(self, day: date, hour: int, events: list[Event]) -> QWidget:
        cell = _HourCell()
        cell.setObjectName("agendaHourCell")
        cell.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        for event in events[:2]:
            pill = QLabel(f"{event.start.strftime('%H:%M')} {self._truncate(event.title)}")
            pill.setObjectName("eventPill")
            pill.setStyleSheet(f"background-color: {event.color}; color: #0B0F16;")
            layout.addWidget(pill)

        if len(events) > 2:
            more = QLabel(f"+{len(events) - 2}")
            more.setObjectName("dayCellMore")
            layout.addWidget(more)

        layout.addStretch(1)
        cell.clicked.connect(lambda d=day, h=hour: self._open_day_dialog(d, f"{h:02d}:00"))
        return cell

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------

    def _shift_month(self, delta: int) -> None:
        month = self.month_cursor.month + delta
        year = self.month_cursor.year
        if month < 1:
            month, year = 12, year - 1
        elif month > 12:
            month, year = 1, year + 1
        self.month_cursor = self.month_cursor.replace(year=year, month=month, day=1)
        self._render_month_calendar()

    def _shift_week(self, delta: int) -> None:
        self.week_cursor = self.week_cursor + timedelta(days=7 * delta)
        self._render_week_planner()

    def _go_today(self) -> None:
        self.today = datetime.now().date()
        self.month_cursor = self.today.replace(day=1)
        self.week_cursor = self.today
        self._refresh_all()

    def _refresh_all(self) -> None:
        self._render_month_calendar()
        self._render_week_planner()

    # ------------------------------------------------------------------
    # Diálogo de evento
    # ------------------------------------------------------------------

    def _open_day_dialog(self, day: date, default_time: str = "09:00") -> None:
        dialog = EventDialog(self.agenda_manager, day, default_time, parent=self)
        dialog.events_changed.connect(self._refresh_all)
        dialog.exec()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_show(self) -> None:
        super().on_show()
        self._refresh_all()

    @staticmethod
    def _capitalized_month(reference: date) -> str:
        text = reference.strftime("%B %Y")
        return text[:1].upper() + text[1:]

    @staticmethod
    def _truncate(title: str, limit: int = 18) -> str:
        clean = str(title or "Evento").strip()
        return clean if len(clean) <= limit else f"{clean[: limit - 1]}…"