from __future__ import annotations

from datetime import date, timedelta

import customtkinter as ctk

from backend.database.conexao import conectar
from frontend.telas.base_screen import BaseScreen

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except Exception:  # pragma: no cover
    FigureCanvasTkAgg = None
    Figure = None


class DashboardScreen(BaseScreen):
    title = "Dashboard"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        self.xp_progress = ctk.CTkProgressBar(
            self.content,
            height=16,
            fg_color="#1a1a1a",
            progress_color="#00FFFF",
            corner_radius=8,
        )
        self.xp_progress.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 6))

        self.xp_label = ctk.CTkLabel(
            self.content,
            text="XP 0/100",
            text_color="#00FFFF",
            font=("Segoe UI", 13, "bold"),
        )
        self.xp_label.grid(row=1, column=0, sticky="w", padx=6, pady=(0, 12))

        stats = ctk.CTkFrame(self.content, fg_color="transparent")
        stats.grid(row=2, column=0, sticky="ew", padx=2)
        for col in range(4):
            stats.grid_columnconfigure(col, weight=1, uniform="stats")

        self.focus_today = self._stat_card(stats, "Tempo focado hoje", 0)
        self.sessions_today = self._stat_card(stats, "Sessões de foco", 1)
        self.last_session = self._stat_card(stats, "Última sessão", 2)
        self.productivity = self._stat_card(stats, "Produtividade", 3)

        self.chart_wrap = ctk.CTkFrame(self.content, fg_color="#111111", corner_radius=14)
        self.chart_wrap.grid(row=3, column=0, sticky="nsew", padx=2, pady=(12, 0))
        self.chart_wrap.grid_columnconfigure(0, weight=1)
        self.chart_wrap.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.chart_wrap,
            text="Gráfico Semanal",
            font=("Segoe UI", 16, "bold"),
            text_color="#00FFFF",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self.chart_host = ctk.CTkFrame(self.chart_wrap, fg_color="#111111")
        self.chart_host.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def on_show(self) -> None:
        super().on_show()
        data = self._load_metrics()
        self._render_stats(data)
        self._render_chart(data["weekly"])

    def _stat_card(self, parent, title: str, col: int) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(card, text=title, text_color="#8fdede", font=("Segoe UI", 12)).pack(anchor="w", padx=12, pady=(10, 4))
        value = ctk.CTkLabel(card, text="--", text_color="#FFFFFF", font=("Segoe UI", 20, "bold"))
        value.pack(anchor="w", padx=12, pady=(0, 10))
        return value

    def _load_metrics(self) -> dict:
        today = date.today()
        weekly = []
        result = {
            "minutes": 0,
            "sessions": 0,
            "last": "--:--",
            "productivity": "0%",
            "weekly": weekly,
        }
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS minutes,
                       COUNT(*) AS sessions,
                       MAX(fim) AS last_end
                FROM pomodoro
                WHERE DATE(inicio) = DATE(?)
                """,
                (today.isoformat(),),
            )
            row = cursor.fetchone()
            if row:
                result["minutes"] = int(row["minutes"])
                result["sessions"] = int(row["sessions"])
                if row["last_end"]:
                    result["last"] = str(row["last_end"])[11:16]

            cursor.execute("SELECT COUNT(*) AS total FROM tarefas")
            total_tasks = int(cursor.fetchone()["total"])
            cursor.execute("SELECT COUNT(*) AS total FROM tarefas WHERE status = 'concluida'")
            done_tasks = int(cursor.fetchone()["total"])
            if total_tasks > 0:
                result["productivity"] = f"{int((done_tasks / total_tasks) * 100)}%"

            for offset in range(6, -1, -1):
                day = today - timedelta(days=offset)
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(duracao_min), 0) AS minutes
                    FROM pomodoro
                    WHERE DATE(inicio) = DATE(?)
                    """,
                    (day.isoformat(),),
                )
                weekly.append((day.strftime("%a"), int(cursor.fetchone()["minutes"])))

            conn.close()
        except Exception:
            pass
        return result

    def _render_stats(self, data: dict) -> None:
        self.focus_today.configure(text=f"{data['minutes']} min")
        self.sessions_today.configure(text=str(data["sessions"]))
        self.last_session.configure(text=str(data["last"]))
        self.productivity.configure(text=str(data["productivity"]))

        xp = min(100, int(data["minutes"] * 2))
        self.xp_progress.set(xp / 100)
        self.xp_label.configure(text=f"XP {xp}/100")

    def _render_chart(self, weekly: list[tuple[str, int]]) -> None:
        for child in self.chart_host.winfo_children():
            child.destroy()

        if Figure is None or FigureCanvasTkAgg is None:
            ctk.CTkLabel(
                self.chart_host,
                text="matplotlib não disponível no ambiente.",
                text_color="#FFFFFF",
            ).pack(pady=20)
            return

        figure = Figure(figsize=(6, 2.6), dpi=100, facecolor="#111111")
        ax = figure.add_subplot(111)
        ax.set_facecolor("#111111")

        labels = [item[0] for item in weekly]
        values = [item[1] for item in weekly]
        bars = ax.bar(labels, values, color="#00FFFF")
        for bar in bars:
            bar.set_alpha(0.8)

        ax.tick_params(axis="x", colors="#FFFFFF")
        ax.tick_params(axis="y", colors="#FFFFFF")
        ax.spines["bottom"].set_color("#00FFFF")
        ax.spines["left"].set_color("#00FFFF")
        ax.spines["top"].set_color("#111111")
        ax.spines["right"].set_color("#111111")
        ax.set_ylabel("Minutos", color="#FFFFFF")

        canvas = FigureCanvasTkAgg(figure, master=self.chart_host)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
