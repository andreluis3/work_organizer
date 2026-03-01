from __future__ import annotations

import customtkinter as ctk

from frontend.services.metrics import MetricsService
from frontend.telas.base_screen import BaseScreen
from frontend.widgets.cards import StatCard


class DashboardScreen(BaseScreen):
    title = "Dashboard"

    def __init__(self, master, controller):
        super().__init__(master, controller)

        action_bar = ctk.CTkFrame(self.header, fg_color="transparent")
        action_bar.grid(row=0, column=1, sticky="e")

        self.new_task_btn = ctk.CTkButton(
            action_bar,
            text="+ Nova tarefa",
            height=34,
            corner_radius=8,
            fg_color="#2b74ff",
            hover_color="#215fd8",
            command=self._on_new_task,
        )
        self.new_task_btn.pack()

        self.cards_grid = ctk.CTkFrame(self.content, fg_color="transparent")
        self.cards_grid.pack(fill="both", expand=True)
        self.cards_grid.bind("<Configure>", self._on_grid_resize)

        self.cards: dict[str, StatCard] = {
            "tarefas_hoje": StatCard(self.cards_grid, "Tarefas de hoje", "0", "Agenda diária"),
            "tarefas_pendentes": StatCard(self.cards_grid, "Pendentes", "0", "Prioridade ativa"),
            "foco_hoje": StatCard(self.cards_grid, "Focus Time", "0 min", "Sessões pomodoro"),
            "produtividade": StatCard(self.cards_grid, "Produtividade", "0%", "Execução do dia"),
        }

        self._layout_cards(columns=2)

    def on_show(self) -> None:
        super().on_show()
        self._refresh_metrics()
        self._pulse_button()

    def _on_new_task(self) -> None:
        self.controller.toast("Fluxo de criação de tarefa disponível em breve.", level="info")

    def _refresh_metrics(self) -> None:
        data = MetricsService.dashboard_metrics()
        self.cards["tarefas_hoje"].set_value(data["tarefas_hoje"], icon="\u25cf")
        self.cards["tarefas_pendentes"].set_value(data["tarefas_pendentes"], icon="\u26a0")
        self.cards["foco_hoje"].set_value(data["foco_hoje"], icon="\u23f1")
        self.cards["produtividade"].set_value(data["produtividade"], icon="\u25b2")

    def _on_grid_resize(self, event) -> None:
        width = event.width
        if width < 560:
            columns = 1
        elif width < 980:
            columns = 2
        else:
            columns = 4
        self._layout_cards(columns)

    def _layout_cards(self, columns: int) -> None:
        for widget in self.cards_grid.winfo_children():
            widget.grid_forget()

        for col in range(columns):
            self.cards_grid.grid_columnconfigure(col, weight=1, uniform="dashboard")

        for index, card in enumerate(self.cards.values()):
            row = index // columns
            col = index % columns
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

    def _pulse_button(self) -> None:
        colors = ["#2b74ff", "#3a84ff", "#2b74ff"]

        def animate(step: int = 0):
            if step >= len(colors):
                return
            self.new_task_btn.configure(fg_color=colors[step])
            self.after(90, lambda: animate(step + 1))

        animate()
