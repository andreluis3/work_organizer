# frontend/pyqt_ui/dialogs/event_dialog.py
"""
Diálogo de eventos de um dia específico da agenda.

Equivalente ao modal `_open_add_event()` do antigo AgendaScreen (CustomTkinter).
Não contém regra de negócio: toda validação de horário e persistência em
memória é delegada ao AgendaManager (core/agenda_manager.py).
"""

from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.agenda_manager import AgendaManager, Event

PRIORITIES = ["Alta", "Média", "Baixa"]

PRIORITY_COLORS = {
    "Alta": "#F87171",
    "Média": "#FACC15",
    "Baixa": "#38BDF8",
}


class EventDialog(QDialog):
    """Mostra e gerencia os eventos de um dia. Fecha sozinho ao salvar/excluir."""

    events_changed = pyqtSignal()

    def __init__(
        self,
        agenda_manager: AgendaManager,
        day: date,
        default_time: str = "09:00",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.agenda_manager = agenda_manager
        self.day = day
        self.default_time = default_time

        self.setWindowTitle(f"Eventos - {day.strftime('%d/%m/%Y')}")
        self.setMinimumSize(480, 640)
        self.setModal(True)

        self._build_ui()
        self._render_events_list()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel(self.day.strftime("%d/%m/%Y"))
        title.setObjectName("dialogTitle")
        root.addWidget(title)

        root.addWidget(self._section_label("Eventos do dia"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(180)
        self.events_container = QWidget()
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setContentsMargins(0, 0, 0, 0)
        self.events_layout.setSpacing(6)
        self.events_layout.addStretch(1)
        scroll.setWidget(self.events_container)
        root.addWidget(scroll)

        root.addWidget(self._build_form())

        self.status_label = QLabel("")
        self.status_label.setObjectName("dialogStatus")
        root.addWidget(self.status_label)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Salvar Evento")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save_event)
        buttons_row.addWidget(close_btn)
        buttons_row.addWidget(save_btn)
        root.addLayout(buttons_row)

    def _build_form(self) -> QWidget:
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(8)

        form_layout.addWidget(self._section_label("Novo evento"))

        form_layout.addWidget(QLabel("Título"))
        self.title_input = QLineEdit()
        form_layout.addWidget(self.title_input)

        time_row = QHBoxLayout()
        start_col = QVBoxLayout()
        start_col.addWidget(QLabel("Hora início (HH:MM)"))
        self.start_input = QLineEdit(self.default_time)
        start_col.addWidget(self.start_input)

        end_col = QVBoxLayout()
        end_col.addWidget(QLabel("Hora fim (HH:MM)"))
        self.end_input = QLineEdit(self._default_end_time(self.default_time))
        end_col.addWidget(self.end_input)

        time_row.addLayout(start_col)
        time_row.addLayout(end_col)
        form_layout.addLayout(time_row)

        meta_row = QHBoxLayout()
        priority_col = QVBoxLayout()
        priority_col.addWidget(QLabel("Prioridade"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(PRIORITIES)
        self.priority_combo.setCurrentText("Média")
        priority_col.addWidget(self.priority_combo)

        category_col = QVBoxLayout()
        category_col.addWidget(QLabel("Categoria"))
        self.category_input = QLineEdit("Trabalho")
        category_col.addWidget(self.category_input)

        meta_row.addLayout(priority_col)
        meta_row.addLayout(category_col)
        form_layout.addLayout(meta_row)

        form_layout.addWidget(QLabel("Descrição"))
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)
        form_layout.addWidget(self.description_input)

        return form_frame

    def _section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    # ------------------------------------------------------------------
    # Lista de eventos do dia
    # ------------------------------------------------------------------

    def _render_events_list(self) -> None:
        while self.events_layout.count() > 1:
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        events = self.agenda_manager.get_events_day(self.day)

        if not events:
            empty = QLabel("Nenhum evento cadastrado para este dia.")
            empty.setObjectName("emptyHint")
            self.events_layout.insertWidget(0, empty)
            return

        for index, event in enumerate(events):
            self.events_layout.insertWidget(index, self._build_event_row(event))

    def _build_event_row(self, event: Event) -> QWidget:
        row = QFrame()
        row.setObjectName("eventRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)

        time_label = QLabel(f"{event.start.strftime('%H:%M')} - {event.end.strftime('%H:%M')}")
        time_label.setObjectName("eventTime")
        time_label.setFixedWidth(100)
        layout.addWidget(time_label)

        title_label = QLabel(self._truncate(event.title))
        title_label.setObjectName("eventTitle")
        layout.addWidget(title_label, stretch=1)

        delete_btn = QPushButton("Excluir")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda _checked, event_id=event.id: self._delete_event(event_id))
        layout.addWidget(delete_btn)

        return row

    def _delete_event(self, event_id: int | None) -> None:
        if event_id is None:
            return
        self.agenda_manager.remove_event(event_id)
        self._render_events_list()
        self.events_changed.emit()

    # ------------------------------------------------------------------
    # Salvar novo evento
    # ------------------------------------------------------------------

    def _save_event(self) -> None:
        title = self.title_input.text().strip() or "Evento"
        category = self.category_input.text().strip() or "Geral"
        priority = self.priority_combo.currentText().strip() or "Média"
        description = self.description_input.toPlainText().strip()

        try:
            start_dt = self.agenda_manager.build_datetime(self.day, self.start_input.text().strip())
            end_dt = self.agenda_manager.build_datetime(self.day, self.end_input.text().strip())
        except ValueError:
            self.status_label.setText("Use horário no formato HH:MM.")
            return

        try:
            self.agenda_manager.add_event(
                Event(
                    title=title,
                    start=start_dt,
                    end=end_dt,
                    priority=priority,
                    category=category,
                    description=description,
                    color=PRIORITY_COLORS.get(priority, "#38BDF8"),
                )
            )
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        self.events_changed.emit()
        self.accept()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _truncate(title: str, limit: int = 40) -> str:
        clean = str(title or "Evento").strip()
        return clean if len(clean) <= limit else f"{clean[: limit - 1]}…"

    @staticmethod
    def _default_end_time(start_time: str) -> str:
        try:
            hour, minute = start_time.strip().split(":")
            total_minutes = int(hour) * 60 + int(minute) + 60
            return f"{(total_minutes // 60) % 24:02d}:{total_minutes % 60:02d}"
        except ValueError:
            return "10:00"