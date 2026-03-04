from __future__ import annotations

from dataclasses import dataclass
from datetime import date as dt_date
from datetime import datetime, timedelta
import calendar
import customtkinter as ctk


@dataclass(slots=True)
class Event:
    title: str
    date: dt_date
    start_time: str
    end_time: str
    priority: str = "Social"
    recurrence: str = "none"  # none, weekly, monthly, yearly


class Agenda(ctk.CTkFrame):
    WEEKDAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    PRIORITY_COLORS = {
        "urgente": "#E74C3C",
        "recorrente": "#F1C40F",
        "trabalho": "#F1C40F",
        "social": "#3498DB",
        "aniversario": "#2ECC71",
        "aniversário": "#2ECC71",
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#0b1220", corner_radius=14, **kwargs)
        self.current_date = datetime.now()
        self.events: list[Event] = []
        self.view_mode = ctk.StringVar(value="Mês")

        self.filter_urgent_var = ctk.BooleanVar(value=True)
        self.filter_recurrent_var = ctk.BooleanVar(value=True)
        self.filter_social_var = ctk.BooleanVar(value=True)

        self._day_base_colors: dict[ctk.CTkFrame, str] = {}
        self._next_events_labels: list[ctk.CTkLabel] = []
        self._next_birthdays_labels: list[ctk.CTkLabel] = []

        self.grid_columnconfigure(0, weight=7, uniform="planner")
        self.grid_columnconfigure(1, weight=3, uniform="planner")
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_calendar()
        self._refresh_calendar()

    def _build_header(self) -> None:
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 10))
        self.header.grid_columnconfigure(1, weight=1)

        self.prev_button = ctk.CTkButton(
            self.header,
            text="<",
            width=34,
            height=32,
            command=lambda: self._shift_period(-1),
            fg_color="#1d293f",
            hover_color="#273854",
        )
        self.prev_button.grid(row=0, column=0, padx=(0, 8))

        self.title_label = ctk.CTkLabel(
            self.header,
            text="",
            font=("Segoe UI", 20, "bold"),
            text_color="#E2E8F0",
        )
        self.title_label.grid(row=0, column=1, sticky="w")

        self.next_button = ctk.CTkButton(
            self.header,
            text=">",
            width=34,
            height=32,
            command=lambda: self._shift_period(1),
            fg_color="#1d293f",
            hover_color="#273854",
        )
        self.next_button.grid(row=0, column=2, padx=8)

        self.view_toggle = ctk.CTkSegmentedButton(
            self.header,
            values=["Mês", "Semana"],
            variable=self.view_mode,
            command=lambda _: self._refresh_calendar(),
            fg_color="#1d293f",
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
            unselected_color="#1d293f",
            unselected_hover_color="#273854",
        )
        self.view_toggle.grid(row=0, column=3, sticky="e")

    def _build_calendar(self) -> None:
        self.left_column = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=14)
        self.left_column.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=(0, 16))
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure(1, weight=1)

        self.weekday_header = ctk.CTkFrame(self.left_column, fg_color="#111c31", corner_radius=10)
        self.weekday_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        self.calendar_body = ctk.CTkFrame(self.left_column, fg_color="transparent")
        self.calendar_body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.calendar_body.grid_columnconfigure(0, weight=1)
        self.calendar_body.grid_rowconfigure(0, weight=1)

        self.right_column = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=14)
        self.right_column.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(0, 16))
        self.right_column.grid_columnconfigure(0, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)

        self.new_event_button = ctk.CTkButton(
            self.right_column,
            text="Novo Evento",
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self._open_event_modal(self.current_date.date()),
        )
        self.new_event_button.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        self.side_scroll = ctk.CTkScrollableFrame(
            self.right_column,
            fg_color="transparent",
            corner_radius=0,
        )
        self.side_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.side_scroll.grid_columnconfigure(0, weight=1)

        filters_title = ctk.CTkLabel(
            self.side_scroll,
            text="Filtros de prioridade",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        filters_title.grid(row=0, column=0, sticky="ew", pady=(4, 8))

        self.chk_urgent = ctk.CTkCheckBox(
            self.side_scroll,
            text="Urgente",
            variable=self.filter_urgent_var,
            command=self._refresh_calendar,
        )
        self.chk_urgent.grid(row=1, column=0, sticky="w", pady=2)

        self.chk_recurrent = ctk.CTkCheckBox(
            self.side_scroll,
            text="Recorrente",
            variable=self.filter_recurrent_var,
            command=self._refresh_calendar,
        )
        self.chk_recurrent.grid(row=2, column=0, sticky="w", pady=2)

        self.chk_social = ctk.CTkCheckBox(
            self.side_scroll,
            text="Social",
            variable=self.filter_social_var,
            command=self._refresh_calendar,
        )
        self.chk_social.grid(row=3, column=0, sticky="w", pady=(2, 12))

        upcoming_title = ctk.CTkLabel(
            self.side_scroll,
            text="Próximos Eventos",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        upcoming_title.grid(row=4, column=0, sticky="ew", pady=(8, 6))

        self.upcoming_box = ctk.CTkFrame(self.side_scroll, fg_color="#0b1424", corner_radius=10)
        self.upcoming_box.grid(row=5, column=0, sticky="ew")
        self.upcoming_box.grid_columnconfigure(0, weight=1)

        birthdays_title = ctk.CTkLabel(
            self.side_scroll,
            text="Próximos Aniversários",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        birthdays_title.grid(row=6, column=0, sticky="ew", pady=(12, 6))

        self.birthdays_box = ctk.CTkFrame(self.side_scroll, fg_color="#0b1424", corner_radius=10)
        self.birthdays_box.grid(row=7, column=0, sticky="ew", pady=(0, 6))
        self.birthdays_box.grid_columnconfigure(0, weight=1)

    def _refresh_calendar(self) -> None:
        self._update_header_title()
        self._clear_container(self.weekday_header)
        self._clear_container(self.calendar_body)

        if self.view_mode.get() == "Semana":
            self._render_week_view()
        else:
            self._render_month_view()

        self._render_sidebar_lists()

    def _render_month_view(self) -> None:
        for idx, weekday in enumerate(self.WEEKDAY_LABELS):
            lbl = ctk.CTkLabel(
                self.weekday_header,
                text=weekday,
                font=("Segoe UI", 12, "bold"),
                text_color="#94A3B8",
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=8)
            self.weekday_header.grid_columnconfigure(idx, weight=1)

        month_grid = ctk.CTkFrame(self.calendar_body, fg_color="transparent")
        month_grid.grid(row=0, column=0, sticky="nsew")
        for col in range(7):
            month_grid.grid_columnconfigure(col, weight=1, uniform="month")
        for row in range(6):
            month_grid.grid_rowconfigure(row, weight=1, uniform="month")

        month_matrix = calendar.Calendar(firstweekday=0).monthdatescalendar(
            self.current_date.year, self.current_date.month
        )
        while len(month_matrix) < 6:
            month_matrix.append([month_matrix[-1][-1] + timedelta(days=i + 1) for i in range(7)])

        for row_idx, week in enumerate(month_matrix):
            for col_idx, day_date in enumerate(week):
                is_current_month = day_date.month == self.current_date.month
                is_today = day_date == datetime.now().date()
                base_color = "#13203a" if is_current_month else "#101a2e"
                if is_today:
                    base_color = "#1E3A8A"

                day_frame = ctk.CTkFrame(
                    month_grid,
                    fg_color=base_color,
                    corner_radius=10,
                    border_width=1 if is_today else 0,
                    border_color="#60A5FA" if is_today else "transparent",
                )
                day_frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=3, pady=3)
                day_frame.grid_columnconfigure(0, weight=1)
                day_frame.grid_rowconfigure(1, weight=1)

                num_color = "#E2E8F0" if is_current_month else "#64748B"
                day_num = ctk.CTkLabel(
                    day_frame,
                    text=str(day_date.day),
                    font=("Segoe UI", 13, "bold"),
                    text_color=num_color,
                    anchor="w",
                )
                day_num.grid(row=0, column=0, sticky="nw", padx=8, pady=(6, 2))

                indicators_host = ctk.CTkFrame(day_frame, fg_color="transparent")
                indicators_host.grid(row=1, column=0, sticky="sew", padx=8, pady=(2, 8))
                indicators_host.grid_columnconfigure(0, weight=1)
                self._add_event_indicators(indicators_host, day_date)

                self._bind_day_interactions(day_frame, day_date, base_color)

    def _render_week_view(self) -> None:
        week_start = self.current_date.date() - timedelta(days=self.current_date.weekday())
        week_days = [week_start + timedelta(days=i) for i in range(7)]

        week_header = ctk.CTkFrame(self.weekday_header, fg_color="transparent")
        week_header.grid(row=0, column=0, sticky="ew")
        for idx, label in enumerate(["Hora"] + self.WEEKDAY_LABELS):
            txt = label
            if idx > 0:
                current_day = week_days[idx - 1]
                txt = f"{label} {current_day.day:02d}/{current_day.month:02d}"
            ctk.CTkLabel(
                week_header,
                text=txt,
                font=("Segoe UI", 11, "bold"),
                text_color="#94A3B8",
            ).grid(row=0, column=idx, sticky="ew", padx=2, pady=8)
            week_header.grid_columnconfigure(idx, weight=1)

        timeline = ctk.CTkFrame(self.calendar_body, fg_color="transparent")
        timeline.grid(row=0, column=0, sticky="nsew")
        timeline.grid_columnconfigure(0, weight=1)
        for col in range(1, 8):
            timeline.grid_columnconfigure(col, weight=2, uniform="week")
        timeline.grid_rowconfigure(0, weight=1)

        time_column = ctk.CTkFrame(timeline, fg_color="#0d1729", corner_radius=10)
        time_column.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        day_columns: list[ctk.CTkFrame] = []

        timeline_height = 560
        hours = list(range(8, 23))
        total_minutes = (22 - 8) * 60

        for hour in hours:
            pos_y = int(((hour - 8) * 60 / total_minutes) * timeline_height)
            ctk.CTkLabel(
                time_column,
                text=f"{hour:02d}:00",
                font=("Segoe UI", 10),
                text_color="#93A4C5",
            ).place(x=8, y=pos_y - 6)

        for idx, day_date in enumerate(week_days):
            col = ctk.CTkFrame(timeline, fg_color="#13203a", corner_radius=10)
            col.grid(row=0, column=idx + 1, sticky="nsew", padx=2)
            col.grid_propagate(False)
            col.configure(height=timeline_height)
            day_columns.append(col)

            for hour in range(8, 23):
                line_y = int((((hour - 8) * 60) / total_minutes) * timeline_height)
                ctk.CTkFrame(col, fg_color="#1E293B", height=1).place(relx=0.04, rely=0, y=line_y, relwidth=0.92)

            self._bind_day_interactions(col, day_date, "#13203a")
            self._render_week_events_for_day(col, day_date, timeline_height)

    def _render_week_events_for_day(self, day_column: ctk.CTkFrame, day_date: dt_date, timeline_height: int) -> None:
        total_minutes = (22 - 8) * 60
        start_window = 8 * 60
        events = self._filter_events(self._get_events_for_date(day_date))
        for event in events:
            start_min, end_min = self._event_minutes(event)
            start_min = max(start_min, start_window)
            end_min = min(end_min, 22 * 60)
            if end_min <= start_min:
                continue

            y = ((start_min - start_window) / total_minutes) * timeline_height
            h = max(28, ((end_min - start_min) / total_minutes) * timeline_height)
            color = self._priority_color(event.priority)
            block = ctk.CTkFrame(day_column, fg_color=color, corner_radius=8)
            block.place(x=6, y=y + 1, relwidth=0.92, height=h - 2)

            label = ctk.CTkLabel(
                block,
                text=f"{event.start_time} {event.title}",
                font=("Segoe UI", 10, "bold"),
                text_color="#07121F",
                anchor="w",
            )
            label.pack(fill="x", padx=6, pady=4)

    def _add_event_indicators(self, day_frame: ctk.CTkFrame, target_date: dt_date) -> None:
        day_events = self._filter_events(self._get_events_for_date(target_date))
        if not day_events:
            return

        for idx, event in enumerate(day_events[:3]):
            ctk.CTkFrame(
                day_frame,
                fg_color=self._priority_color(event.priority),
                corner_radius=3,
                height=4,
            ).grid(row=idx, column=0, sticky="ew", pady=2)

        if len(day_events) > 3:
            ctk.CTkLabel(
                day_frame,
                text=f"+{len(day_events) - 3}",
                font=("Segoe UI", 10, "bold"),
                text_color="#94A3B8",
                anchor="w",
            ).grid(row=3, column=0, sticky="w", pady=(2, 0))

    def _open_event_modal(self, selected_date: dt_date) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("Novo Evento")
        modal.geometry("380x360")
        modal.grab_set()

        ctk.CTkLabel(modal, text="Título").grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        title_entry = ctk.CTkEntry(modal, width=320)
        title_entry.grid(row=1, column=0, padx=16, pady=(0, 8))

        ctk.CTkLabel(modal, text="Data (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", padx=16, pady=(4, 4))
        date_entry = ctk.CTkEntry(modal, width=320)
        date_entry.insert(0, selected_date.strftime("%Y-%m-%d"))
        date_entry.grid(row=3, column=0, padx=16, pady=(0, 8))

        ctk.CTkLabel(modal, text="Hora início (HH:MM)").grid(row=4, column=0, sticky="w", padx=16, pady=(4, 4))
        start_entry = ctk.CTkEntry(modal, width=320)
        start_entry.insert(0, "09:00")
        start_entry.grid(row=5, column=0, padx=16, pady=(0, 8))

        ctk.CTkLabel(modal, text="Hora fim (HH:MM)").grid(row=6, column=0, sticky="w", padx=16, pady=(4, 4))
        end_entry = ctk.CTkEntry(modal, width=320)
        end_entry.insert(0, "10:00")
        end_entry.grid(row=7, column=0, padx=16, pady=(0, 8))

        ctk.CTkLabel(modal, text="Prioridade").grid(row=8, column=0, sticky="w", padx=16, pady=(4, 4))
        priority_box = ctk.CTkComboBox(modal, values=["Urgente", "Recorrente", "Social", "Aniversario"])
        priority_box.set("Social")
        priority_box.grid(row=9, column=0, padx=16, pady=(0, 8))

        ctk.CTkLabel(modal, text="Recorrência").grid(row=10, column=0, sticky="w", padx=16, pady=(4, 4))
        recurrence_box = ctk.CTkComboBox(modal, values=["none", "weekly", "monthly", "yearly"])
        recurrence_box.set("none")
        recurrence_box.grid(row=11, column=0, padx=16, pady=(0, 12))

        status_label = ctk.CTkLabel(modal, text="", text_color="#F87171")
        status_label.grid(row=12, column=0, sticky="w", padx=16, pady=(0, 8))

        def save_event() -> None:
            try:
                event_date = datetime.strptime(date_entry.get().strip(), "%Y-%m-%d").date()
                datetime.strptime(start_entry.get().strip(), "%H:%M")
                datetime.strptime(end_entry.get().strip(), "%H:%M")
            except ValueError:
                status_label.configure(text="Data ou hora inválida.")
                return

            if end_entry.get().strip() <= start_entry.get().strip():
                status_label.configure(text="Hora fim deve ser maior que início.")
                return

            title = title_entry.get().strip() or "Evento"
            self.events.append(
                Event(
                    title=title,
                    date=event_date,
                    start_time=start_entry.get().strip(),
                    end_time=end_entry.get().strip(),
                    priority=priority_box.get().strip(),
                    recurrence=recurrence_box.get().strip(),
                )
            )
            modal.destroy()
            self._refresh_calendar()

        ctk.CTkButton(
            modal,
            text="Salvar Evento",
            command=save_event,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=("Segoe UI", 13, "bold"),
        ).grid(row=13, column=0, sticky="ew", padx=16, pady=(0, 14))

    def _get_events_for_date(self, target_date: dt_date) -> list[Event]:
        matched: list[Event] = []
        for event in self.events:
            if event.date == target_date:
                matched.append(event)
                continue
            if event.recurrence == "weekly" and event.date.weekday() == target_date.weekday():
                matched.append(event)
                continue
            if event.recurrence == "monthly" and event.date.day == target_date.day:
                matched.append(event)
                continue
            if (
                event.recurrence == "yearly"
                and event.date.day == target_date.day
                and event.date.month == target_date.month
            ):
                matched.append(event)
        return matched

    def _filter_events(self, events: list[Event]) -> list[Event]:
        active = self._active_priority_filter_set()
        if not active:
            return events
        filtered: list[Event] = []
        for event in events:
            normalized = self._normalize_priority(event.priority)
            if normalized in active:
                filtered.append(event)
        return filtered

    def _active_priority_filter_set(self) -> set[str]:
        active: set[str] = set()
        if self.filter_urgent_var.get():
            active.add("urgente")
        if self.filter_recurrent_var.get():
            active.update({"recorrente", "trabalho"})
        if self.filter_social_var.get():
            active.update({"social", "aniversario", "aniversário"})
        return active

    def _render_sidebar_lists(self) -> None:
        self._clear_container(self.upcoming_box)
        self._clear_container(self.birthdays_box)
        self._next_events_labels.clear()
        self._next_birthdays_labels.clear()

        upcoming = self._collect_upcoming_events(limit=8)
        if not upcoming:
            lbl = ctk.CTkLabel(self.upcoming_box, text="Sem eventos próximos", text_color="#7C8BA3")
            lbl.grid(row=0, column=0, sticky="w", padx=10, pady=8)
            self._next_events_labels.append(lbl)
        else:
            for idx, (target_date, event) in enumerate(upcoming):
                label = ctk.CTkLabel(
                    self.upcoming_box,
                    text=f"{target_date.strftime('%d/%m')} • {event.start_time} • {event.title}",
                    text_color="#D4DEEE",
                    anchor="w",
                    justify="left",
                )
                label.grid(row=idx, column=0, sticky="ew", padx=10, pady=4)
                self._next_events_labels.append(label)

        birthdays = [(d, e) for d, e in upcoming if self._normalize_priority(e.priority) in {"aniversario", "aniversário"}]
        if not birthdays:
            lbl = ctk.CTkLabel(self.birthdays_box, text="Nenhum aniversário próximo", text_color="#7C8BA3")
            lbl.grid(row=0, column=0, sticky="w", padx=10, pady=8)
            self._next_birthdays_labels.append(lbl)
        else:
            for idx, (target_date, event) in enumerate(birthdays[:4]):
                label = ctk.CTkLabel(
                    self.birthdays_box,
                    text=f"{target_date.strftime('%d/%m')} • {event.title}",
                    text_color="#D4DEEE",
                    anchor="w",
                )
                label.grid(row=idx, column=0, sticky="ew", padx=10, pady=4)
                self._next_birthdays_labels.append(label)

    def _collect_upcoming_events(self, limit: int = 8) -> list[tuple[dt_date, Event]]:
        results: list[tuple[dt_date, Event]] = []
        cursor = self.current_date.date()
        for offset in range(0, 90):
            day = cursor + timedelta(days=offset)
            events = self._filter_events(self._get_events_for_date(day))
            for event in sorted(events, key=lambda e: e.start_time):
                results.append((day, event))
                if len(results) >= limit:
                    return results
        return results

    def _shift_period(self, step: int) -> None:
        if self.view_mode.get() == "Semana":
            self.current_date += timedelta(days=7 * step)
        else:
            year = self.current_date.year
            month = self.current_date.month + step
            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1
            max_day = calendar.monthrange(year, month)[1]
            new_day = min(self.current_date.day, max_day)
            self.current_date = self.current_date.replace(year=year, month=month, day=new_day)
        self._refresh_calendar()

    def _update_header_title(self) -> None:
        if self.view_mode.get() == "Semana":
            week_start = self.current_date.date() - timedelta(days=self.current_date.weekday())
            week_end = week_start + timedelta(days=6)
            title = f"Semana {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}"
        else:
            title = self.current_date.strftime("%B %Y").capitalize()
        self.title_label.configure(text=title)

    def _bind_day_interactions(self, day_frame: ctk.CTkFrame, day_date: dt_date, base_color: str) -> None:
        self._day_base_colors[day_frame] = base_color
        hover_color = self._mix_colors(base_color, "#FFFFFF", 0.08)
        click_color = self._mix_colors(base_color, "#FFFFFF", 0.18)

        def on_enter(_event) -> None:
            day_frame.configure(fg_color=hover_color)

        def on_leave(_event) -> None:
            day_frame.configure(fg_color=base_color)

        def on_click(_event) -> None:
            day_frame.configure(fg_color=click_color)
            self.after(110, lambda: day_frame.configure(fg_color=hover_color))
            self.after(210, lambda: day_frame.configure(fg_color=base_color))
            self._open_event_modal(day_date)

        day_frame.bind("<Enter>", on_enter)
        day_frame.bind("<Leave>", on_leave)
        day_frame.bind("<Button-1>", on_click)
        for child in day_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            child.bind("<Button-1>", on_click)

    def _event_minutes(self, event: Event) -> tuple[int, int]:
        start = datetime.strptime(event.start_time, "%H:%M")
        end = datetime.strptime(event.end_time, "%H:%M")
        return start.hour * 60 + start.minute, end.hour * 60 + end.minute

    def _priority_color(self, priority: str) -> str:
        return self.PRIORITY_COLORS.get(self._normalize_priority(priority), "#60A5FA")

    @staticmethod
    def _normalize_priority(priority: str) -> str:
        return priority.strip().lower()

    @staticmethod
    def _clear_container(container) -> None:
        for child in container.winfo_children():
            child.destroy()

    @staticmethod
    def _mix_colors(color_a: str, color_b: str, alpha: float) -> str:
        a_r, a_g, a_b = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
        b_r, b_g, b_b = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
        r = round((1 - alpha) * a_r + alpha * b_r)
        g = round((1 - alpha) * a_g + alpha * b_g)
        b = round((1 - alpha) * a_b + alpha * b_b)
        return f"#{r:02X}{g:02X}{b:02X}"
