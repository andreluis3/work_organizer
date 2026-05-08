from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
import customtkinter as ctk

from core.agenda_manager import AgendaManager, Event
from frontend.telas.base_screen import BaseScreen


class AgendaScreen(BaseScreen):
    title = "Agenda"

    WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    PRIORITIES = ["Alta", "Média", "Baixa"]

    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.agenda = AgendaManager()
        self.today = datetime.now().date()
        self.month_cursor = self.today.replace(day=1)
        self.week_cursor = self.today

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.content, fg_color="#0d1526", segmented_button_fg_color="#17263f")
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.calendar_tab = self.tabview.add("Calendário")
        self.week_tab = self.tabview.add("Planner Semanal")

        self._build_calendar_tab()
        self._build_week_tab()
        self._refresh_all()

    def _build_calendar_tab(self) -> None:
        self.calendar_tab.grid_columnconfigure(0, weight=1)
        self.calendar_tab.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self.calendar_tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(top, text="<", width=36, command=lambda: self._shift_month(-1)).grid(row=0, column=0)
        self.month_label = ctk.CTkLabel(top, text="", font=("Segoe UI", 20, "bold"), anchor="w")
        self.month_label.grid(row=0, column=1, sticky="w", padx=10)

        nav = ctk.CTkFrame(top, fg_color="transparent")
        nav.grid(row=0, column=2, sticky="e")
        ctk.CTkButton(nav, text="Hoje", width=62, command=self._go_today).pack(side="left", padx=(0, 6))
        ctk.CTkButton(nav, text=">", width=36, command=lambda: self._shift_month(1)).pack(side="left")

        self.weekdays_header = ctk.CTkFrame(self.calendar_tab, fg_color="#111b2f", corner_radius=10)
        self.weekdays_header.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        for idx, day in enumerate(self.WEEKDAYS):
            self.weekdays_header.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(
                self.weekdays_header,
                text=day,
                font=("Segoe UI", 12, "bold"),
                text_color="#9fb0cc",
            ).grid(row=0, column=idx, sticky="ew", pady=8)

        self.month_grid = ctk.CTkFrame(self.calendar_tab, fg_color="transparent")
        self.month_grid.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        for col in range(7):
            self.month_grid.grid_columnconfigure(col, weight=1, uniform="month")
        for row in range(6):
            self.month_grid.grid_rowconfigure(row, weight=1, uniform="month")

    def _build_week_tab(self) -> None:
        self.week_tab.grid_columnconfigure(0, weight=1)
        self.week_tab.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self.week_tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(top, text="<", width=36, command=lambda: self._shift_week(-1)).grid(row=0, column=0)
        self.week_label = ctk.CTkLabel(top, text="", font=("Segoe UI", 18, "bold"), anchor="w")
        self.week_label.grid(row=0, column=1, sticky="w", padx=10)

        nav = ctk.CTkFrame(top, fg_color="transparent")
        nav.grid(row=0, column=2, sticky="e")
        ctk.CTkButton(nav, text="Hoje", width=62, command=self._go_today).pack(side="left", padx=(0, 6))
        ctk.CTkButton(nav, text=">", width=36, command=lambda: self._shift_week(1)).pack(side="left")

        self.week_scroll = ctk.CTkScrollableFrame(self.week_tab, fg_color="#0b1220")
        self.week_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.week_scroll.grid_columnconfigure(0, weight=1)

    def _refresh_all(self) -> None:
        self._render_month_calendar()
        self._render_week_planner()

    def _render_month_calendar(self) -> None:
        self.month_label.configure(text=self.month_cursor.strftime("%B %Y").capitalize())

        for child in self.month_grid.winfo_children():
            child.destroy()

        cal = calendar.Calendar(firstweekday=0)
        matrix = cal.monthdatescalendar(self.month_cursor.year, self.month_cursor.month)
        while len(matrix) < 6:
            matrix.append([matrix[-1][-1].fromordinal(matrix[-1][-1].toordinal() + i + 1) for i in range(7)])

        for row_idx, week in enumerate(matrix[:6]):
            for col_idx, day in enumerate(week):
                in_month = day.month == self.month_cursor.month
                is_today = day == self.today
                bg = "#13203a" if in_month else "#0f1a2e"
                if is_today:
                    bg = "#1a3263"

                card = ctk.CTkFrame(
                    self.month_grid,
                    fg_color=bg,
                    border_width=1,
                    border_color="#3f557a" if is_today else "#23344f",
                    corner_radius=8,
                )
                card.grid(row=row_idx, column=col_idx, sticky="nsew", padx=3, pady=3)
                card.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    card,
                    text=str(day.day),
                    font=("Segoe UI", 12, "bold"),
                    text_color="#eff4ff" if in_month else "#7787a5",
                    anchor="w",
                ).grid(row=0, column=0, sticky="nw", padx=8, pady=(6, 3))

                events = self.agenda.get_events_day(day)
                for idx, event in enumerate(events[:3], start=1):
                    evt = ctk.CTkLabel(
                        card,
                        text=self._event_title_preview(event.title),
                        fg_color=event.color,
                        text_color="#0b0f16",
                        corner_radius=8,
                        padx=8,
                        pady=2,
                        anchor="w",
                        font=("Segoe UI", 10, "bold"),
                    )
                    evt.grid(row=idx, column=0, sticky="ew", padx=8, pady=2)
                    self._bind_hover(evt, event.color)

                if len(events) > 3:
                    ctk.CTkLabel(
                        card,
                        text=f"+{len(events) - 3} eventos",
                        text_color="#8ea2c2",
                        font=("Segoe UI", 10),
                        anchor="w",
                    ).grid(row=4, column=0, sticky="w", padx=8, pady=(2, 4))

                self._bind_day_click(card, day)

    def _render_week_planner(self) -> None:
        for child in self.week_scroll.winfo_children():
            child.destroy()

        week_days = self.agenda.week_days(self.week_cursor)
        week_start, week_end = week_days[0], week_days[-1]
        self.week_label.configure(text=f"Semana {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}")

        grid = ctk.CTkFrame(self.week_scroll, fg_color="transparent")
        grid.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        grid.grid_columnconfigure(0, weight=0)
        for col in range(1, 8):
            grid.grid_columnconfigure(col, weight=1, uniform="week")

        ctk.CTkLabel(grid, text="Hora", font=("Segoe UI", 11, "bold"), text_color="#98a9c7").grid(
            row=0, column=0, sticky="nsew", padx=2, pady=(0, 6)
        )

        for idx, day in enumerate(week_days, start=1):
            caption = f"{self.WEEKDAYS[idx - 1]}\n{day.strftime('%d/%m')}"
            head = ctk.CTkFrame(grid, fg_color="#111c31", corner_radius=8)
            head.grid(row=0, column=idx, sticky="nsew", padx=2, pady=(0, 6))
            ctk.CTkLabel(head, text=caption, font=("Segoe UI", 11, "bold"), text_color="#d7e3f6").pack(
                padx=8, pady=6
            )

        events_week = self.agenda.get_events_for_week(self.week_cursor)
        events_index: dict[tuple[date, int], list[Event]] = {}
        for event in events_week:
            key = (event.start.date(), event.start.hour)
            events_index.setdefault(key, []).append(event)

        for hour in range(8, 23):
            row = (hour - 8) + 1
            ctk.CTkLabel(grid, text=f"{hour:02d}:00", text_color="#8ca0c0", font=("Segoe UI", 10)).grid(
                row=row, column=0, sticky="ne", padx=(0, 6), pady=2
            )

            for col, day in enumerate(week_days, start=1):
                cell = ctk.CTkFrame(grid, fg_color="#121e34", corner_radius=8, border_width=1, border_color="#203250")
                cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                cell.grid_columnconfigure(0, weight=1)

                for idx, event in enumerate(events_index.get((day, hour), [])[:2]):
                    evt = ctk.CTkLabel(
                        cell,
                        text=f"{event.start.strftime('%H:%M')} {self._event_title_preview(event.title)}",
                        fg_color=event.color,
                        text_color="#0b0f16",
                        corner_radius=8,
                        padx=6,
                        pady=2,
                        anchor="w",
                        font=("Segoe UI", 9, "bold"),
                    )
                    evt.grid(row=idx, column=0, sticky="ew", padx=4, pady=2)
                    self._bind_hover(evt, event.color)

                if len(events_index.get((day, hour), [])) > 2:
                    ctk.CTkLabel(
                        cell,
                        text=f"+{len(events_index[(day, hour)]) - 2}",
                        text_color="#91a8cc",
                        font=("Segoe UI", 9),
                    ).grid(row=2, column=0, sticky="w", padx=4)

                self._bind_day_click(cell, day, default_time=f"{hour:02d}:00")

    def _shift_month(self, delta: int) -> None:
        month = self.month_cursor.month + delta
        year = self.month_cursor.year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        self.month_cursor = self.month_cursor.replace(year=year, month=month, day=1)
        self._render_month_calendar()

    def _shift_week(self, delta: int) -> None:
        self.week_cursor = self.week_cursor.fromordinal(self.week_cursor.toordinal() + (7 * delta))
        self._render_week_planner()

    def _go_today(self) -> None:
        self.today = datetime.now().date()
        self.month_cursor = self.today.replace(day=1)
        self.week_cursor = self.today
        self._refresh_all()

    def _bind_day_click(self, widget, target_day: date, default_time: str = "09:00") -> None:
        def handle_click(_event=None) -> None:
            self._open_add_event(target_day, default_time)

        widget.bind("<Button-1>", handle_click)
        for child in widget.winfo_children():
            child.bind("<Button-1>", handle_click)

    def _open_add_event(self, selected_day: date, default_time: str = "09:00") -> None:
        modal = ctk.CTkToplevel(self)
        modal.title(f"Eventos - {selected_day.strftime('%d/%m/%Y')}")
        modal.geometry("500x650")
        modal.minsize(460, 560)
        modal.transient(self.winfo_toplevel())

        # Centralizar a janela na tela
        modal.update_idletasks()
        width = modal.winfo_width()
        height = modal.winfo_height()
        screen_width = modal.winfo_screenwidth()
        screen_height = modal.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

        modal.attributes("-topmost", True)
        modal.focus_set()

        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkScrollableFrame(
            modal,
            fg_color="#0b1220",
            scrollbar_button_color="#1F2937",
            scrollbar_button_hover_color="#334155",
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=selected_day.strftime("%d/%m/%Y"),
            font=("Segoe UI", 22, "bold"),
            text_color="#f8fbff",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Fechar",
            width=78,
            fg_color="#1f2937",
            hover_color="#334155",
            command=modal.destroy,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            frame,
            text="Eventos do dia",
            font=("Segoe UI", 15, "bold"),
            text_color="#d7e3f6",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        events_frame = ctk.CTkFrame(frame, fg_color="transparent")
        events_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 14))
        events_frame.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(frame, fg_color="#111b2f", corner_radius=12, border_width=1, border_color="#203250")
        form.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 4))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            form,
            text="Novo evento",
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 10))

        ctk.CTkLabel(form, text="Título", text_color="#9fb0cc").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 4)
        )
        title_entry = ctk.CTkEntry(form, height=38)
        title_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16)

        ctk.CTkLabel(form, text="Hora início (HH:MM)", text_color="#9fb0cc").grid(
            row=3, column=0, sticky="w", padx=16, pady=(12, 4)
        )
        start_entry = ctk.CTkEntry(form, height=38)
        start_entry.insert(0, default_time)
        start_entry.grid(row=4, column=0, sticky="ew", padx=(16, 8))

        ctk.CTkLabel(form, text="Hora fim (HH:MM)", text_color="#9fb0cc").grid(
            row=3, column=1, sticky="w", padx=8, pady=(12, 4)
        )
        end_entry = ctk.CTkEntry(form, height=38)
        end_entry.insert(0, self._default_end_time(default_time))
        end_entry.grid(row=4, column=1, sticky="ew", padx=(8, 16))

        ctk.CTkLabel(form, text="Prioridade", text_color="#9fb0cc").grid(
            row=5, column=0, sticky="w", padx=16, pady=(12, 4)
        )
        priority_box = ctk.CTkComboBox(form, values=self.PRIORITIES, height=38)
        priority_box.set("Média")
        priority_box.grid(row=6, column=0, sticky="ew", padx=(16, 8))

        ctk.CTkLabel(form, text="Categoria", text_color="#9fb0cc").grid(
            row=5, column=1, sticky="w", padx=8, pady=(12, 4)
        )
        category_entry = ctk.CTkEntry(form, height=38)
        category_entry.insert(0, "Trabalho")
        category_entry.grid(row=6, column=1, sticky="ew", padx=(8, 16))

        ctk.CTkLabel(form, text="Descrição", text_color="#9fb0cc").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4)
        )
        description_box = ctk.CTkTextbox(form, height=100, fg_color="#0d1526", border_width=1, border_color="#263449")
        description_box.grid(row=8, column=0, columnspan=2, sticky="ew", padx=16)

        status = ctk.CTkLabel(form, text="", text_color="#ff6b6b", anchor="w")
        status.grid(row=9, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 4))

        def render_day_events() -> None:
            for child in events_frame.winfo_children():
                child.destroy()

            events = self.agenda.get_events_day(selected_day)
            if not events:
                ctk.CTkLabel(
                    events_frame,
                    text="Nenhum evento cadastrado para este dia.",
                    text_color="#8ea2c2",
                    font=("Segoe UI", 12),
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=2, pady=4)
                return

            for row, event in enumerate(events):
                item = ctk.CTkFrame(
                    events_frame,
                    fg_color="#111b2f",
                    corner_radius=10,
                    border_width=1,
                    border_color="#203250",
                )
                item.grid(row=row, column=0, sticky="ew", pady=4)
                item.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    item,
                    text=self._event_time_label(event),
                    text_color="#38bdf8",
                    font=("Segoe UI", 12, "bold"),
                    width=98,
                    anchor="w",
                ).grid(row=0, column=0, sticky="w", padx=(10, 6), pady=8)

                ctk.CTkLabel(
                    item,
                    text=self._event_title_preview(event.title),
                    text_color="#f8fbff",
                    font=("Segoe UI", 12, "bold"),
                    anchor="w",
                ).grid(row=0, column=1, sticky="ew", padx=4, pady=8)

                ctk.CTkButton(
                    item,
                    text="Excluir",
                    width=72,
                    height=28,
                    fg_color="#7f1d1d",
                    hover_color="#991b1b",
                    text_color="#fee2e2",
                    command=lambda event_id=event.id: remove_event(event_id),
                ).grid(row=0, column=2, sticky="e", padx=(6, 10), pady=8)

        def remove_event(event_id: int | None) -> None:
            if event_id is None:
                return
            self.agenda.remove_event(event_id)
            render_day_events()
            self._refresh_all()
            self._show_toast("Evento removido.", level="success")

        def save_event() -> None:
            title = title_entry.get().strip() or "Evento"
            category = category_entry.get().strip() or "Geral"
            priority = priority_box.get().strip() or "Média"
            description = description_box.get("1.0", "end").strip()

            try:
                start_dt = self.agenda.build_datetime(selected_day, start_entry.get().strip())
                end_dt = self.agenda.build_datetime(selected_day, end_entry.get().strip())
            except ValueError:
                status.configure(text="Use horário no formato HH:MM.")
                return

            if end_dt <= start_dt:
                status.configure(text="A hora final deve ser maior que a inicial.")
                return

            try:
                self.agenda.add_event(
                    Event(
                        title=title,
                        start=start_dt,
                        end=end_dt,
                        priority=priority,
                        category=category,
                        description=description,
                        color=self._priority_color(priority),
                    )
                )
            except ValueError as exc:
                status.configure(text=str(exc))
                return

            modal.destroy()
            self._refresh_all()
            self._show_toast("Evento salvo na agenda.", level="success")

        save_btn = ctk.CTkButton(
            form,
            text="Salvar Evento",
            height=40,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#03130b",
            command=save_event,
        )
        save_btn.grid(row=10, column=0, columnspan=2, sticky="ew", padx=16, pady=(8, 16))

        render_day_events()
        title_entry.focus()

    def _show_toast(self, message: str, level: str = "info") -> None:
        if hasattr(self.controller, "toast"):
            self.controller.toast(message, level=level)

    @staticmethod
    def _event_title_preview(title: str, limit: int = 20) -> str:
        clean = str(title or "Evento").strip()
        return clean if len(clean) <= limit else f"{clean[:limit - 1]}…"

    @staticmethod
    def _event_time_label(event: Event) -> str:
        return f"[{event.start.strftime('%H:%M')} - {event.end.strftime('%H:%M')}]"

    @staticmethod
    def _default_end_time(start_time: str) -> str:
        try:
            base = datetime.strptime(start_time.strip(), "%H:%M")
        except ValueError:
            return "10:00"
        return (base + timedelta(hours=1)).strftime("%H:%M")

    @staticmethod
    def _priority_color(priority: str) -> str:
        colors = {
            "Alta": "#F87171",
            "Média": "#FACC15",
            "Baixa": "#38BDF8",
        }
        return colors.get(priority, "#38BDF8")

    @staticmethod
    def _bind_hover(widget: ctk.CTkBaseClass, base_color: str) -> None:
        hover_color = AgendaScreen._mix_color(base_color, "#FFFFFF", 0.16)

        def on_enter(_event=None) -> None:
            widget.configure(fg_color=hover_color)

        def on_leave(_event=None) -> None:
            widget.configure(fg_color=base_color)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    @staticmethod
    def _mix_color(color_a: str, color_b: str, alpha: float) -> str:
        ar, ag, ab = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
        br, bg, bb = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
        rr = round((1 - alpha) * ar + alpha * br)
        rg = round((1 - alpha) * ag + alpha * bg)
        rb = round((1 - alpha) * ab + alpha * bb)
        return f"#{rr:02X}{rg:02X}{rb:02X}"
