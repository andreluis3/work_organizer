from __future__ import annotations

import customtkinter as ctk

from backend.pomodoro_manager import PomodoroManager
from frontend.telas.base_screen import BaseScreen


class FocusTimeScreen(BaseScreen):
    title = "Focus Time"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.pomodoro = PomodoroManager()
        self._timer_job = None

        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self.content, fg_color="#0b1220", corner_radius=18)
        card.grid(row=0, column=0, sticky="n", pady=(20, 0))
        card.grid_columnconfigure(0, weight=1)

        self.mode_label = ctk.CTkLabel(
            card,
            text="FOCUS MODE",
            font=("Segoe UI", 15, "bold"),
            text_color="#9cb0cf",
        )
        self.mode_label.grid(row=0, column=0, pady=(26, 10), padx=30)

        self.timer_label = ctk.CTkLabel(
            card,
            text="25:00",
            font=("Segoe UI", 72, "bold"),
            text_color="#f8fbff",
        )
        self.timer_label.grid(row=1, column=0, padx=30, pady=(0, 20))

        self.progress = ctk.CTkProgressBar(
            card,
            width=360,
            height=14,
            corner_radius=10,
            progress_color="#2b74ff",
            fg_color="#182538",
        )
        self.progress.grid(row=2, column=0, padx=30, pady=(0, 26), sticky="ew")
        self.progress.set(0)

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.grid(row=3, column=0, pady=(0, 28))

        self.start_btn = ctk.CTkButton(
            button_row,
            text="Start",
            width=104,
            height=38,
            corner_radius=12,
            fg_color="#2b74ff",
            hover_color="#215fd8",
            command=self.pomodoro.iniciar,
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = ctk.CTkButton(
            button_row,
            text="Pause",
            width=104,
            height=38,
            corner_radius=12,
            fg_color="#22395e",
            hover_color="#1a2d4a",
            command=self.pomodoro.pausar,
        )
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.reset_btn = ctk.CTkButton(
            button_row,
            text="Reset",
            width=104,
            height=38,
            corner_radius=12,
            fg_color="#22395e",
            hover_color="#1a2d4a",
            command=self._reset_and_refresh,
        )
        self.reset_btn.grid(row=0, column=2, padx=6)

        self._refresh_ui()
        self._schedule_tick()

    def on_show(self) -> None:
        super().on_show()
        self._refresh_ui()

    def _schedule_tick(self) -> None:
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
        self._timer_job = self.after(1000, self._tick)

    def _tick(self) -> None:
        self.pomodoro.atualizar()
        self._refresh_ui()
        self._timer_job = self.after(1000, self._tick)

    def _reset_and_refresh(self) -> None:
        self.pomodoro.resetar()
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        total_seconds = max(0, self.pomodoro.segundos_restantes)
        minutos = total_seconds // 60
        segundos = total_seconds % 60
        self.timer_label.configure(text=f"{minutos:02d}:{segundos:02d}")
        self.mode_label.configure(text="FOCUS MODE" if self.pomodoro.modo_foco else "BREAK MODE")
        self.progress.set(self.pomodoro.progresso())
