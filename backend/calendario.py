from dataclasses import dataclass
from datetime import date, datetime, timedelta
import customtkinter as ctk
import calendar

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List


@dataclass
class Event:
    title: str
    start: datetime
    end: datetime

    id: int | None = None
    description: str = ""
    prioridade: str = "Média"
    categoria: str = "geral"
    color: str = "#4CAF50"
    recurring: bool = False


class AgendaManager:

    def __init__(self):
        self.events: List[Event] = []

    # adicionar evento
    def add_event(self, event: Event):
        self.events.append(event)

    # remover evento pelo id
    def remove_event(self, event_id: int):
        self.events = [e for e in self.events if e.id != event_id]

    # -------------------------
    # eventos de um dia
    # -------------------------
    def get_events_day(self, day: date):

        result = []

        for event in self.events:
            if event.start.date() <= day <= event.end.date():
                result.append(event)

        return result

    # alias para compatibilidade com frontend
    def get_events_for_day(self, day: date):
        return self.get_events_day(day)

    # -------------------------
    # dias da semana
    # -------------------------
    def week_days(self, reference: date):

        monday = reference - timedelta(days=reference.weekday())

        week = []
        for i in range(7):
            week.append(monday + timedelta(days=i))

        return week

    # -------------------------
    # eventos da semana
    # -------------------------
    def get_events_for_week(self, reference: date):

        week = self.week_days(reference)

        events_week = []

        for event in self.events:
            if event.start.date() in week:
                events_week.append(event)

        return events_week

    # -------------------------
    # eventos do mês
    # -------------------------
    def get_events_month(self, year: int, month: int):

        events_month = []

        for event in self.events:
            if event.start.year == year and event.start.month == month:
                events_month.append(event)

        return events_month

class Agenda(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.events = [] # Aqui você carregaria seus dados
        self.current_date = datetime.now()
        
        # Configuração de colunas para expandirem igualmentes
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=20, pady=10) 
        self._refresh_calendar()

    def _refresh_calendar(self):
        # Limpa o calendário anterior
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Nomes dos dias
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for i, dia in enumerate(dias_semana):
            lbl = ctk.CTkLabel(self.calendar_frame, text=dia, font=("Segoe UI", 12, "bold"))
            lbl.grid(row=0, column=i, sticky="nsew", pady=5)

        # Matriz do mês
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day != 0:
                    # Criamos um "Card" para cada dia
                    day_card = ctk.CTkFrame(self.calendar_frame, border_width=1, border_color="#333333")
                    day_card.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=2, pady=2)
                    
                    # Número do dia
                    lbl_num = ctk.CTkLabel(day_card, text=str(day), font=("Segoe UI", 11))
                    lbl_num.pack(anchor="ne", padx=5)

                    # Lógica simples de verificação de eventos
                    self._render_events_in_day(day_card, day)
                    
                    # Tornar o card clicável para adicionar evento
                    day_card.bind("<Button-1>", lambda e, d=day: self._open_add_event(d))

    def _render_events_in_day(self, parent_frame, day):
        # Exemplo de como mostrar uma "pílula" de prioridade
        # Aqui você filtraria self.events pela data
        pass

    def _open_add_event(self, day):
        # Aqui você criaria um ctk.CTkToplevel para o formulário
        print(f"Abrindo formulário para o dia {day}")

    def _build_header(self):
        header = ctk.CTkFrame(self)
        header.pack(fill="x", pady=10)

        self.month_label = ctk.CTkLabel(header, text="", font=("Segoe UI", 20))
        self.month_label.pack(side="left", padx=20)

        prev_btn = ctk.CTkButton(header, text="<", width=40, command=self._prev_month)
        prev_btn.pack(side="right", padx=5)

        next_btn = ctk.CTkButton(header, text=">", width=40, command=self._next_month)
        next_btn.pack(side="right", padx=5)

        self._update_month_label()

    def _update_month_label(self):
        self.month_label.configure(
            text=self.current_date.strftime("%B %Y")
        )

    def _prev_month(self):
        month = self.current_date.month - 1 or 12
        year = self.current_date.year - 1 if month == 12 else self.current_date.year
        self.current_date = self.current_date.replace(year=year, month=month)
        self._refresh_calendar()

    def _next_month(self):
        month = self.current_date.month + 1 if self.current_date.month < 12 else 1
        year = self.current_date.year + 1 if month == 1 else self.current_date.year
        self.current_date = self.current_date.replace(year=year, month=month)
        self._refresh_calendar()

    def _build_calendar(self):
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=20)

        self._refresh_calendar()