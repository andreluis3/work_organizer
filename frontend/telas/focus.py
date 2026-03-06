from __future__ import annotations

from datetime import date
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from backend.database.conexao import conectar
from backend.pomodoro_manager import PomodoroManager
from frontend.telas.base_screen import BaseScreen


class FocusScreen(BaseScreen):
    title = "Focus"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.pomodoro = PomodoroManager()
        self._job = None
        self._tree_images = self._load_tree_images()

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        shell = ctk.CTkFrame(self.content, fg_color="#0b0b0b", corner_radius=16)
        shell.grid(row=0, column=0, sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(2, weight=1)

        self.xp_progress = ctk.CTkProgressBar(
            shell,
            height=14,
            fg_color="#1a1a1a",
            progress_color="#00FFFF",
            corner_radius=8,
        )
        self.xp_progress.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 6))
        self.xp_progress.set(0)

        self.xp_label = ctk.CTkLabel(
            shell,
            text="XP 0/100",
            font=("Segoe UI", 13, "bold"),
            text_color="#00FFFF",
        )
        self.xp_label.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 10))

        center = ctk.CTkFrame(shell, fg_color="transparent")
        center.grid(row=2, column=0, sticky="nsew", padx=18, pady=6)
        center.grid_columnconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=2)
        center.grid_columnconfigure(2, weight=1)
        center.grid_rowconfigure(0, weight=1)

        self.left_stats = ctk.CTkFrame(center, fg_color="#1a1a1a", corner_radius=14)
        self.left_stats.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_stats.grid_columnconfigure(0, weight=1)

        self.right_forest = ctk.CTkFrame(center, fg_color="#1a1a1a", corner_radius=14)
        self.right_forest.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        self.right_forest.grid_columnconfigure(0, weight=1)

        main = ctk.CTkFrame(center, fg_color="#111111", corner_radius=14)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)

        self.tree_label = ctk.CTkLabel(main, text="")
        self.tree_label.grid(row=0, column=0, pady=(22, 10))

        self.timer_label = ctk.CTkLabel(
            main,
            text="25:00",
            font=("Consolas", 72, "bold"),
            text_color="#FFFFFF",
        )
        self.timer_label.grid(row=1, column=0, pady=(0, 6))

        self.mode_label = ctk.CTkLabel(
            main,
            text="FOCUS MODE",
            font=("Segoe UI", 15, "bold"),
            text_color="#00FFFF",
        )
        self.mode_label.grid(row=2, column=0, pady=(0, 14))

        controls = ctk.CTkFrame(shell, fg_color="transparent")
        controls.grid(row=3, column=0, pady=(12, 20))
        ctk.CTkButton(
            controls,
            text="Start",
            width=120,
            fg_color="#00FFFF",
            hover_color="#00d8d8",
            text_color="#0b0b0b",
            command=self.pomodoro.iniciar,
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            controls,
            text="Pause",
            width=120,
            fg_color="#1a1a1a",
            hover_color="#232323",
            border_width=1,
            border_color="#00FFFF",
            command=self.pomodoro.pausar,
        ).grid(row=0, column=1, padx=6)
        ctk.CTkButton(
            controls,
            text="Reset",
            width=120,
            fg_color="#1a1a1a",
            hover_color="#232323",
            border_width=1,
            border_color="#00FFFF",
            command=self._reset_focus,
        ).grid(row=0, column=2, padx=6)

        self.minutes_label = ctk.CTkLabel(self.left_stats, text="", text_color="#FFFFFF", font=("Segoe UI", 14))
        self.sessions_label = ctk.CTkLabel(self.left_stats, text="", text_color="#FFFFFF", font=("Segoe UI", 14))
        self.last_label = ctk.CTkLabel(self.left_stats, text="", text_color="#FFFFFF", font=("Segoe UI", 14))
        self.minutes_label.grid(row=0, column=0, sticky="w", padx=14, pady=(16, 8))
        self.sessions_label.grid(row=1, column=0, sticky="w", padx=14, pady=8)
        self.last_label.grid(row=2, column=0, sticky="w", padx=14, pady=(8, 16))

        self._refresh_forest()
        self._refresh_metrics()
        self._refresh_ui()
        self._tick()

    def on_show(self) -> None:
        super().on_show()
        self._refresh_metrics()
        self._refresh_forest()
        self._refresh_ui()

    def _tick(self) -> None:
        self.pomodoro.atualizar()
        self._refresh_ui()
        self._job = self.after(1000, self._tick)

    def _reset_focus(self) -> None:
        self.pomodoro.resetar()
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        seconds = max(self.pomodoro.segundos_restantes, 0)
        mm, ss = divmod(seconds, 60)
        self.timer_label.configure(text=f"{mm:02d}:{ss:02d}")
        self.mode_label.configure(text="FOCUS MODE" if self.pomodoro.modo_foco else "BREAK MODE")

        if self.pomodoro.modo_foco:
            progress = self.pomodoro.progresso()
        else:
            progress = 1 - self.pomodoro.progresso()
        self._set_tree_stage(progress)
        self._set_xp(progress)

        if not self.pomodoro.rodando and self.pomodoro.modo_foco and seconds == self.pomodoro.tempo_foco:
            self._refresh_metrics()
            self._refresh_forest()

    def _set_tree_stage(self, progress: float) -> None:
        pct = progress * 100
        if pct >= 92:
            index = 3
        elif pct >= 70:
            index = 2
        elif pct >= 50:
            index = 1
        elif pct >= 25:
            index = 0
        else:
            index = -1

        if index == -1:
            self.tree_label.configure(text="seedling...", image=None, text_color="#00FFFF", font=("Segoe UI", 14))
            return
        self.tree_label.configure(image=self._tree_images[index], text="")

    def _set_xp(self, progress: float) -> None:
        xp = int(min(100, progress * 100))
        self.xp_progress.set(xp / 100)
        self.xp_label.configure(text=f"XP {xp}/100")

    def _refresh_metrics(self) -> None:
        stats = self._today_stats()
        self.minutes_label.configure(text=f"Tempo focado hoje: {stats['minutes']} min")
        self.sessions_label.configure(text=f"Sessões de foco: {stats['sessions']}")
        self.last_label.configure(text=f"Última sessão: {stats['last']}")

    def _refresh_forest(self) -> None:
        for widget in self.right_forest.winfo_children():
            widget.destroy()

        sessions = self._today_stats()["sessions"]
        ctk.CTkLabel(
            self.right_forest,
            text="Floresta de Hoje",
            text_color="#00FFFF",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        count = max(1, min(12, sessions))
        for idx in range(count):
            image = self._tree_images[min(idx // 3, 3)]
            lbl = ctk.CTkLabel(self.right_forest, text="", image=image)
            row = (idx // 3) + 1
            col = idx % 3
            self.right_forest.grid_columnconfigure(col, weight=1)
            lbl.grid(row=row, column=col, padx=6, pady=6)

    def _today_stats(self) -> dict[str, str | int]:
        result = {"minutes": 0, "sessions": 0, "last": "--:--"}
        try:
            conn = conectar()
            cursor = conn.cursor()
            today = date.today().isoformat()
            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS minutes,
                       COUNT(*) AS sessions,
                       MAX(fim) AS last_end
                FROM pomodoro
                WHERE DATE(inicio) = DATE(?)
                """,
                (today,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                result["minutes"] = int(row["minutes"])
                result["sessions"] = int(row["sessions"])
                if row["last_end"]:
                    result["last"] = str(row["last_end"])[11:16]
        except Exception:
            pass
        return result

    @staticmethod
    def _load_tree_images() -> list[ctk.CTkImage]:
        base = Path(__file__).resolve().parent.parent / "assets" / "focus"
        names = ["tree_1.png", "tree_2.png", "tree_3.png", "tree_4.png"]
        images: list[ctk.CTkImage] = []
        for name in names:
            img = Image.open(base / name)
            images.append(ctk.CTkImage(img, size=(220, 220)))
        return images
