from __future__ import annotations

import customtkinter as ctk

from frontend.telas.base_screen import BaseScreen
from frontend.telas.focus_controller import FocusController


class FocusUIScreen(BaseScreen):
    title = "Focus"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.focus_controller = FocusController(controller)
        self.session_minutes_var = ctk.StringVar(value=str(self.focus_controller.default_minutes))

        self._build_layout()

        self.focus_controller.bind_scheduler(self.after, self.after_cancel)
        self.focus_controller.bind_view(
            on_change=self.render,
            minutes_provider=self.session_minutes_var.get,
            on_reset_input=self._set_session_input,
        )

    def on_show(self) -> None:
        super().on_show()
        self.focus_controller.refresh_from_history()

    def destroy(self) -> None:
        self.focus_controller.destroy()
        super().destroy()

    def _build_layout(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.shell = ctk.CTkFrame(self.content, fg_color="#07131d", corner_radius=22)
        self.shell.grid(row=0, column=0, sticky="nsew")
        self.shell.grid_columnconfigure(0, weight=1)
        self.shell.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.shell, fg_color="#0c1a26", corner_radius=18)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        header.grid_columnconfigure(0, weight=1)

        self.xp_progress = ctk.CTkProgressBar(
            header,
            height=14,
            fg_color="#122433",
            progress_color="#00F5FF",
            corner_radius=8,
        )
        self.xp_progress.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 6))
        self.xp_progress.set(0)

        status_row = ctk.CTkFrame(header, fg_color="transparent")
        status_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))
        status_row.grid_columnconfigure(0, weight=1)

        self.level_label = ctk.CTkLabel(
            status_row,
            text="Foco Nível 1 - Deep Work",
            font=("Segoe UI", 16, "bold"),
            text_color="#d8fbff",
        )
        self.level_label.grid(row=0, column=0, sticky="w")

        self.xp_label = ctk.CTkLabel(
            status_row,
            text="XP 0/100",
            font=("Segoe UI", 13, "bold"),
            text_color="#00F5FF",
        )
        self.xp_label.grid(row=0, column=1, sticky="e")

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self.shell, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=6)
        body.grid_columnconfigure(2, weight=2)

        self._build_metrics_panel(body)
        self._build_center_panel(body)
        self._build_forest_panel(body)

    def _build_metrics_panel(self, parent) -> None:
        panel = ctk.CTkFrame(parent, fg_color="#0c1a26", corner_radius=18)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="METRICAS",
            font=("Share Tech Mono", 16, "bold"),
            text_color="#7dcad0",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))

        self.total_focused_label = self._metric_row(panel, 1, "TEMPO TOTAL FOCADO")
        self.sessions_count_label = self._metric_row(panel, 2, "SESSOES COMPLETAS")
        self.status_chip = ctk.CTkLabel(
            panel,
            text="SISTEMA PRONTO",
            corner_radius=10,
            fg_color="#102736",
            text_color="#9adce2",
            font=("Share Tech Mono", 12, "bold"),
            padx=14,
            pady=8,
        )
        self.status_chip.grid(row=3, column=0, sticky="w", padx=18, pady=(18, 18))

    def _metric_row(self, parent, row: int, title: str) -> ctk.CTkLabel:
        wrap = ctk.CTkFrame(parent, fg_color="#10212e", corner_radius=14)
        wrap.grid(row=row, column=0, sticky="ew", padx=16, pady=8)
        wrap.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrap,
            text=title,
            text_color="#78bfc5",
            font=("Share Tech Mono", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        value = ctk.CTkLabel(
            wrap,
            text="--",
            text_color="#f1feff",
            font=("Share Tech Mono", 24, "bold"),
        )
        value.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))
        return value

    def _build_center_panel(self, parent) -> None:
        self.center_panel = ctk.CTkFrame(parent, fg_color="#091723", corner_radius=22)
        self.center_panel.grid(row=0, column=1, sticky="nsew")
        self.center_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.center_panel,
            text="FOCUS MODE",
            font=("Segoe UI", 15, "bold"),
            text_color="#77b8be",
        ).grid(row=0, column=0, pady=(28, 8))

        timer_wrap = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        timer_wrap.grid(row=1, column=0, pady=(0, 10))

        self.timer_shadow = ctk.CTkLabel(
            timer_wrap,
            text="25:00",
            font=("Orbitron", 78, "bold"),
            text_color="#0a7f86",
        )
        self.timer_shadow.grid(row=0, column=0, padx=(6, 0), pady=(6, 0))

        self.timer_label = ctk.CTkLabel(
            timer_wrap,
            text="25:00",
            font=("Orbitron", 74, "bold"),
            text_color="#00F5FF",
        )
        self.timer_label.grid(row=0, column=0)

        self.progress_bar = ctk.CTkProgressBar(
            self.center_panel,
            width=360,
            height=14,
            corner_radius=8,
            fg_color="#102434",
            progress_color="#00F5FF",
        )
        self.progress_bar.grid(row=2, column=0, padx=42, pady=(10, 20), sticky="ew")
        self.progress_bar.set(0)

        input_row = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        input_row.grid(row=3, column=0, pady=(0, 22))

        ctk.CTkLabel(
            input_row,
            text="Sessao (min)",
            font=("Share Tech Mono", 13, "bold"),
            text_color="#8fd8df",
        ).grid(row=0, column=0, padx=(0, 10))

        self.minutes_entry = ctk.CTkEntry(
            input_row,
            width=90,
            textvariable=self.session_minutes_var,
            justify="center",
            fg_color="#102434",
            border_color="#1fd6df",
            text_color="#efffff",
            font=("Share Tech Mono", 18, "bold"),
        )
        self.minutes_entry.grid(row=0, column=1)

        button_row = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        button_row.grid(row=4, column=0, pady=(0, 28))

        self.primary_button = ctk.CTkButton(
            button_row,
            text="Start",
            width=150,
            height=46,
            corner_radius=14,
            fg_color="#0ec7cf",
            hover_color="#09aab1",
            text_color="#031116",
            border_width=2,
            border_color="#b7fbff",
            font=("Segoe UI", 15, "bold"),
            command=self.focus_controller.handle_primary_action,
        )
        self.primary_button.grid(row=0, column=0, padx=8)

        self.reset_button = ctk.CTkButton(
            button_row,
            text="Reset",
            width=120,
            height=46,
            corner_radius=14,
            fg_color="#102434",
            hover_color="#163244",
            border_width=2,
            border_color="#3f6674",
            text_color="#f3fcff",
            font=("Segoe UI", 15, "bold"),
            command=self.focus_controller.reset_session,
        )
        self.reset_button.grid(row=0, column=1, padx=8)

    def _build_forest_panel(self, parent) -> None:
        panel = ctk.CTkFrame(parent, fg_color="#0c1a26", corner_radius=18)
        panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            panel,
            text="ECOSSISTEMA",
            font=("Share Tech Mono", 16, "bold"),
            text_color="#7dcad0",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        self.forest_message_label = ctk.CTkLabel(
            panel,
            text="Plante sua primeira árvore.",
            text_color="#d9fcff",
            justify="left",
            wraplength=180,
            font=("Segoe UI", 13),
        )
        self.forest_message_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))

        self.forest_grid = ctk.CTkFrame(panel, fg_color="#10212e", corner_radius=14)
        self.forest_grid.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))

    def render(self, view_model: dict) -> None:
        self.timer_label.configure(text=view_model["timer_text"])
        self.timer_shadow.configure(text=view_model["timer_text"])
        self.progress_bar.set(view_model["progress"])

        self.xp_progress.set(view_model["xp_progress"])
        self.xp_label.configure(text=view_model["xp_text"])
        self.level_label.configure(text=view_model["level_text"])

        self.primary_button.configure(text=view_model["primary_label"])
        self.total_focused_label.configure(text=view_model["total_focused"])
        self.sessions_count_label.configure(text=view_model["completed_sessions"])
        self.status_chip.configure(text="EM EXECUCAO" if view_model["is_running"] else "SISTEMA PRONTO")

        self.center_panel.configure(fg_color="#06111b" if view_model["is_running"] else "#091723")
        self.forest_message_label.configure(text=view_model["forest_message"])
        self._render_forest(view_model["forest"])

    def _render_forest(self, forest: list[str]) -> None:
        for child in self.forest_grid.winfo_children():
            child.destroy()

        columns = 5
        for column in range(columns):
            self.forest_grid.grid_columnconfigure(column, weight=1)

        if not forest:
            ctk.CTkLabel(
                self.forest_grid,
                text=".",
                text_color="#10212e",
                font=("Segoe UI", 8),
            ).grid(row=0, column=0, padx=8, pady=8)
            return

        for index, tree in enumerate(forest):
            row = index // columns
            column = index % columns
            ctk.CTkLabel(
                self.forest_grid,
                text=tree,
                font=("Segoe UI Emoji", 24),
            ).grid(row=row, column=column, padx=4, pady=6)

    def _set_session_input(self, minutes: int) -> None:
        self.session_minutes_var.set(str(minutes))
