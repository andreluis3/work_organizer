from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import getpass
import sqlite3

import customtkinter as ctk

from backend import task_manager
from backend.database.conexao import conectar
from frontend.telas.base_screen import BaseScreen
from frontend.telas.forest_system import ForestSystem
from frontend.widgets.cards import StatCard
from typing import List

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvasTkAgg = None
    Figure = None

CYAN = "#00F5FF"
GREEN = "#22C55E"
ORANGE = "#FB923C"
TEXT = "#F8FBFF"
MUTED = "#94A3B8"
SURFACE = "#0B1220"
SURFACE_ALT = "#111827"
BORDER = "#1F2937"
TRACK = "#172036"

LEVEL_TITLES = [
    "Deep Worker",
    "Momentum Builder",
    "Focus Ranger",
    "Flow Architect",
    "Master of Consistency",
]
WEEKDAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]


@dataclass(slots=True)
class DashboardSnapshot:
    user_name: str
    xp: int
    xp_goal: int
    xp_progress: float
    level: int
    title: str
    streak: int
    today_sessions: int
    today_minutes: int
    goal_target: int
    goal_progress: float
    focus_total: str
    productivity: str
    last_session: dict[str, str]
    last_task: dict[str, str]
    current_course: dict[str, str]
    forest: list[str]
    forest_message: str
    week_focus: list[dict[str, int | str]]
    sessions_by_day: list[dict[str, int | str]]
    task_focus: list[dict[str, int | str]]


def get_dynamic_message(snapshot: DashboardSnapshot) -> str:
    remaining = max(0, snapshot.goal_target - snapshot.today_sessions)
    if snapshot.today_sessions == 0:
        return "Bora comecar o dia e plantar sua primeira sessao."
    if snapshot.today_sessions >= snapshot.goal_target:
        return "Meta concluida. Seu ritmo hoje esta forte."
    if snapshot.today_sessions == 1:
        return "Voce ja fez 1 sessao hoje."
    if remaining == 1:
        return "Falta 1 sessao para sua meta."
    return f"Faltam {remaining} sessoes para sua meta."


class DashboardDataProvider:
    def __init__(self) -> None:
        self.sessions_per_level = 4
        self.default_goal_target = 5

    def load_snapshot(self) -> DashboardSnapshot:
        total_minutes = 0
        total_sessions = 0
        today_minutes = 0
        today_sessions = 0
        week_focus: list[dict[str, int | str]] = []
        sessions_by_day: list[dict[str, int | str]] = []
        task_focus: list[dict[str, int | str]] = []
        last_session = self._empty_session()

        try:
            conn = self._connect()
            cursor = conn.cursor()
            last_session = self.get_last_session(cursor)
            today_minutes, today_sessions = self.get_today_sessions(cursor)
            week_focus = self.get_week_data(cursor)
            sessions_by_day = [
                {"label": item["label"], "value": item["sessions"]}
                for item in week_focus
            ]
            task_focus = self.get_task_focus_data(cursor)
            total_minutes, total_sessions = self.get_totals(cursor)
            conn.close()
        except Exception:
            pass

        goal_target = self.get_goal_target()
        level = self.get_level(total_sessions)
        xp = self.get_xp(total_sessions)
        forest_system = ForestSystem()
        forest_system.load_count(total_sessions)

        return DashboardSnapshot(
            user_name=self.get_user_name(),
            xp=xp,
            xp_goal=100,
            xp_progress=xp / 100,
            level=level,
            title=self.get_title(level),
            streak=self.get_streak(),
            today_sessions=today_sessions,
            today_minutes=today_minutes,
            goal_target=goal_target,
            goal_progress=min(1.0, today_sessions / goal_target) if goal_target else 0,
            focus_total=self.format_minutes(total_minutes),
            productivity=self.get_productivity(),
            last_session=last_session,
            last_task=self.get_last_task(),
            current_course=self.get_course_progress(),
            forest=forest_system.get_forest(),
            forest_message=forest_system.get_message(),
            week_focus=week_focus,
            sessions_by_day=sessions_by_day,
            task_focus=task_focus,
        )

    def get_last_session(self, cursor: sqlite3.Cursor) -> dict[str, str]:
        cursor.execute(
            """
            SELECT id, tarefa_id, inicio, fim, duracao_min, observacao
            FROM pomodoro
            ORDER BY datetime(inicio) DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            return self._empty_session()

        task_name = self._resolve_task_name(cursor, row["tarefa_id"], row["observacao"])
        return {
            "duration": f"{int(row['duracao_min'] or 0)} min",
            "task": task_name,
            "time": self._format_clock(row["fim"] or row["inicio"]),
        }

    def get_last_task(self) -> dict[str, str]:
        try:
            tasks = task_manager.get_all_tasks()
        except Exception:
            tasks = []

        if tasks:
            latest = sorted(
                tasks,
                key=lambda item: item.get("updated_at") or item.get("created_at") or "",
                reverse=True,
            )[0]
            progress = self._task_progress(latest)
            return {
                "name": latest.get("title", "Task recente"),
                "progress": progress,
                "status": self._format_task_status(latest.get("status")),
            }

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT titulo, status
                FROM tarefas
                ORDER BY datetime(criada_em) DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                status = str(row["status"] or "pendente").capitalize()
                return {
                    "name": row["titulo"] or "Task recente",
                    "progress": status,
                    "status": status,
                }
        except Exception:
            pass

        return {
            "name": "Nenhuma task recente",
            "progress": "0%",
            "status": "Sem dados",
        }

    def get_course_progress(self) -> dict[str, str]:
        try:
            tasks = [task for task in task_manager.get_all_tasks() if task.get("type") == "course"]
        except Exception:
            tasks = []

        if tasks:
            latest = sorted(
                tasks,
                key=lambda item: item.get("updated_at") or item.get("created_at") or "",
                reverse=True,
            )[0]
            course = latest.get("course") or {}
            progress = int(course.get("progress", 0) or 0)
            lesson = course.get("current_lesson") or "Aula 1"
            total = int(course.get("total_lessons", 0) or 0)
            progress_text = f"{progress}%"
            if total > 0:
                completed = int(round((progress / 100) * total))
                progress_text = f"{completed}/{total} aulas"
            return {
                "name": latest.get("title", "Curso atual"),
                "lesson": lesson,
                "progress": progress_text,
            }

        return {
            "name": "Nenhum curso em andamento",
            "lesson": "Adicione um curso para acompanhar.",
            "progress": "0%",
        }

    def get_today_sessions(self, cursor: sqlite3.Cursor) -> tuple[int, int]:
        today = date.today().isoformat()
        cursor.execute(
            """
            SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
            FROM pomodoro
            WHERE DATE(inicio) = DATE(?)
            """,
            (today,),
        )
        row = cursor.fetchone()
        if not row:
            return 0, 0
        return int(row["minutes"] or 0), int(row["sessions"] or 0)

    def get_week_data(self, cursor: sqlite3.Cursor) -> list[dict[str, int | str]]:
        today = date.today()
        week_rows: list[dict[str, int | str]] = []
        for offset in range(6, -1, -1):
            current_day = today - timedelta(days=offset)
            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
                FROM pomodoro
                WHERE DATE(inicio) = DATE(?)
                """,
                (current_day.isoformat(),),
            )
            row = cursor.fetchone()
            week_rows.append(
                {
                    "label": WEEKDAY_LABELS[current_day.weekday()],
                    "minutes": int(row["minutes"] or 0) if row else 0,
                    "sessions": int(row["sessions"] or 0) if row else 0,
                }
            )
        return week_rows

    def get_xp(self, total_sessions: int) -> int:
        return int((total_sessions % self.sessions_per_level) * (100 / self.sessions_per_level))

    def get_level(self, total_sessions: int) -> int:
        return max(1, (total_sessions // self.sessions_per_level) + 1)

    def get_title(self, level: int) -> str:
        index = min(len(LEVEL_TITLES) - 1, max(0, level - 1))
        return LEVEL_TITLES[index]

    def get_streak(self) -> int:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT DATE(inicio) AS day
                FROM pomodoro
                ORDER BY day DESC
                """
            )
            rows = cursor.fetchall()
            conn.close()
        except Exception:
            return 0

        if not rows:
            return 0

        days = {datetime.strptime(row["day"], "%Y-%m-%d").date() for row in rows if row["day"]}
        streak = 0
        current = date.today()

        if current not in days and (current - timedelta(days=1)) in days:
            current = current - timedelta(days=1)

        while current in days:
            streak += 1
            current -= timedelta(days=1)

        return streak

    def get_task_focus_data(self, cursor: sqlite3.Cursor) -> list[dict[str, int | str]]:
        cursor.execute(
            """
            SELECT tarefa_id, COALESCE(SUM(duracao_min), 0) AS minutes
            FROM pomodoro
            GROUP BY tarefa_id
            ORDER BY minutes DESC
            LIMIT 4
            """
        )
        rows = cursor.fetchall()
        if not rows:
            return []

        data: list[dict[str, int | str]] = []
        for row in rows:
            data.append(
                {
                    "label": self._resolve_task_name(cursor, row["tarefa_id"], "Sem task")[:18],
                    "value": int(row["minutes"] or 0),
                }
            )
        return data

    def get_goal_target(self) -> int:
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT horas_objetivo
                FROM metas
                WHERE (
                    data_inicio IS NULL OR DATE(data_inicio) <= DATE(?)
                ) AND (
                    data_fim IS NULL OR DATE(data_fim) >= DATE(?)
                )
                ORDER BY id DESC
                LIMIT 1
                """,
                (date.today().isoformat(), date.today().isoformat()),
            )
            row = cursor.fetchone()
            conn.close()
            if row and row["horas_objetivo"]:
                return max(1, int(row["horas_objetivo"]))
        except Exception:
            pass
        return self.default_goal_target

    def get_productivity(self) -> str:
        try:
            tasks = task_manager.get_all_tasks()
        except Exception:
            tasks = []

        if tasks:
            completed = sum(1 for task in tasks if task.get("status") == "done")
            total = len(tasks)
            return f"{int((completed / total) * 100) if total else 0}%"

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM tarefas")
            total = int(cursor.fetchone()["total"] or 0)
            cursor.execute("SELECT COUNT(*) AS total FROM tarefas WHERE status = 'concluida'")
            completed = int(cursor.fetchone()["total"] or 0)
            conn.close()
            return f"{int((completed / total) * 100) if total else 0}%"
        except Exception:
            return "0%"

    def get_totals(self, cursor: sqlite3.Cursor) -> tuple[int, int]:
        cursor.execute(
            """
            SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
            FROM pomodoro
            """
        )
        row = cursor.fetchone()
        if not row:
            return 0, 0
        return int(row["minutes"] or 0), int(row["sessions"] or 0)

    def get_user_name(self) -> str:
        raw_name = getpass.getuser().replace("_", " ").strip()
        return raw_name.title() if raw_name else "Usuario"

    def format_minutes(self, minutes: int) -> str:
        hours, remainder = divmod(max(0, minutes), 60)
        if hours:
            return f"{hours}h {remainder:02d}m"
        return f"{remainder} min"

    def _connect(self) -> sqlite3.Connection:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        return conn

    def _empty_session(self) -> dict[str, str]:
        return {
            "duration": "--",
            "task": "Nenhuma sessao concluida ainda",
            "time": "--:--",
        }

    def _format_clock(self, value: str | None) -> str:
        if not value:
            return "--:--"
        try:
            return datetime.fromisoformat(str(value)).strftime("%H:%M")
        except ValueError:
            return str(value)[11:16] if len(str(value)) >= 16 else "--:--"

    def _resolve_task_name(self, cursor: sqlite3.Cursor, task_id: int | None, fallback: str | None) -> str:
        if task_id:
            try:
                cursor.execute("SELECT title FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row and row["title"]:
                    return str(row["title"])
            except Exception:
                pass

            try:
                cursor.execute("SELECT titulo FROM tarefas WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row and row["titulo"]:
                    return str(row["titulo"])
            except Exception:
                pass

        if fallback:
            return str(fallback)
        return "Sessao de foco"

    def _task_progress(self, task: dict) -> str:
        if task.get("type") == "course":
            course = task.get("course") or {}
            return f"{int(course.get('progress', 0) or 0)}%"

        subtasks = task.get("subtasks") or []
        if not subtasks:
            return self._format_task_status(task.get("status"))

        completed = sum(1 for item in subtasks if item.get("completed"))
        total = len(subtasks)
        return f"{int((completed / total) * 100) if total else 0}%"

    def _format_task_status(self, status: str | None) -> str:
        mapping = {
            "done": "Concluida",
            "in_progress": "Em progresso",
            "pending": "Pendente",
            "concluida": "Concluida",
            "pendente": "Pendente",
        }
        return mapping.get(str(status or "").lower(), "Sem status")


class HomeUI(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.data_provider = DashboardDataProvider()
        self.snapshot: DashboardSnapshot | None = None
        self._chart_canvases: List[FigureCanvasTkAgg] = []
        self._streak_color_index = 0
        self._streak_colors = [ORANGE, "#F59E0B", "#FDBA74"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.create_header()
        self.create_hero()
        self.create_charts()
        self.create_goals()
        self.create_forest()
        self.after(500, self._animate_streak)

    def create_header(self) -> None:
        self.header_card = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        self.header_card.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 16))
        self.header_card.grid_columnconfigure(0, weight=1)
        self.header_card.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(self.header_card, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        left.grid_columnconfigure(0, weight=1)

        self.welcome_label = ctk.CTkLabel(
            left,
            text="Bem-vindo de volta",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT,
        )
        self.welcome_label.grid(row=0, column=0, sticky="w")

        self.summary_label = ctk.CTkLabel(
            left,
            text="XP: 0 | Nivel 1 - Deep Worker | 0 dias",
            font=("Segoe UI", 13),
            text_color=MUTED,
        )
        self.summary_label.grid(row=1, column=0, sticky="w", pady=(4, 10))

        self.xp_progress = ctk.CTkProgressBar(
            left,
            height=14,
            corner_radius=999,
            fg_color=TRACK,
            progress_color=CYAN,
        )
        self.xp_progress.grid(row=2, column=0, sticky="ew")
        self.xp_progress.set(0)

        self.xp_caption = ctk.CTkLabel(
            left,
            text="0/100 XP para o proximo nivel",
            font=("Segoe UI", 12),
            text_color=CYAN,
        )
        self.xp_caption.grid(row=3, column=0, sticky="w", pady=(8, 0))

        streak_panel = ctk.CTkFrame(
            self.header_card,
            fg_color="#1A120A",
            corner_radius=18,
            border_width=1,
            border_color="#7C2D12",
        )
        streak_panel.grid(row=0, column=1, sticky="ns", padx=(0, 18), pady=16)

        ctk.CTkLabel(
            streak_panel,
            text="STREAK",
            font=("Segoe UI", 11, "bold"),
            text_color="#FDBA74",
        ).pack(anchor="w", padx=16, pady=(14, 4))

        self.streak_value = ctk.CTkLabel(
            streak_panel,
            text="0 dias",
            font=("Segoe UI", 24, "bold"),
            text_color=ORANGE,
        )
        self.streak_value.pack(anchor="w", padx=16)

        self.streak_hint = ctk.CTkLabel(
            streak_panel,
            text="Mantenha o ritmo hoje.",
            font=("Segoe UI", 12),
            text_color="#FED7AA",
        )
        self.streak_hint.pack(anchor="w", padx=16, pady=(4, 14))

    def create_hero(self) -> None:
        self.hero_card = ctk.CTkFrame(
            self,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        self.hero_card.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 16))
        self.hero_card.grid_columnconfigure(0, weight=1)
        self.hero_card.grid_columnconfigure(1, weight=1)
        self.hero_card.grid_columnconfigure(2, weight=1)

        hero_head = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_head.grid(row=0, column=0, columnspan=3, sticky="ew", padx=18, pady=(16, 10))
        hero_head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero_head,
            text="Resumo do dia",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w")

        self.dynamic_message = ctk.CTkLabel(
            hero_head,
            text="Seu progresso aparece aqui.",
            font=("Segoe UI", 13),
            text_color=CYAN,
        )
        self.dynamic_message.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.last_session_card = StatCard(
            self.hero_card,
            title="Ultima sessao",
            value="--",
            subtitle="Sem registro recente",
            corner_radius=18,
        )
        self.last_session_card.grid(row=1, column=0, sticky="nsew", padx=(18, 8), pady=(0, 18))

        self.last_task_card = StatCard(
            self.hero_card,
            title="Ultima task",
            value="--",
            subtitle="Sem progresso recente",
            corner_radius=18,
        )
        self.last_task_card.grid(row=1, column=1, sticky="nsew", padx=8, pady=(0, 18))

        self.course_card = StatCard(
            self.hero_card,
            title="Curso atual",
            value="--",
            subtitle="Sem curso em andamento",
            corner_radius=18,
        )
        self.course_card.grid(row=1, column=2, sticky="nsew", padx=(8, 18), pady=(0, 18))

    def create_charts(self) -> None:
        self.chart_title = ctk.CTkLabel(
            self,
            text="Analise de foco",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
        )
        self.chart_title.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 10))

        self.focus_chart_card = self._chart_card("Tempo focado | ultimos 7 dias")
        self.focus_chart_card["card"].grid(row=3, column=0, columnspan=2, sticky="nsew", padx=(0, 8), pady=(0, 16))
       
        self.sessions_chart_card = self._chart_card("Sessoes por dia")
        self.sessions_chart_card["card"].grid(row=3, column=2, sticky="nsew", padx=(8, 0), pady=(0, 16))

    def create_goals(self) -> None:
        self.goal_card = ctk.CTkFrame(
            self,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        self.goal_card.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=(0, 8), pady=(0, 16))
        self.goal_card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.goal_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Meta diaria",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w")

        self.goal_value = ctk.CTkLabel(
            header,
            text="0/5 sessoes",
            font=("Segoe UI", 14),
            text_color=CYAN,
        )
        self.goal_value.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.goal_percent = ctk.CTkLabel(
            header,
            text="0%",
            font=("Segoe UI", 24, "bold"),
            text_color=GREEN,
        )
        self.goal_percent.grid(row=0, column=1, rowspan=2, sticky="e")

        self.goal_progress = ctk.CTkProgressBar(
            self.goal_card,
            height=16,
            corner_radius=999,
            fg_color=TRACK,
            progress_color=GREEN,
        )
        self.goal_progress.grid(row=1, column=0, sticky="ew", padx=18)
        self.goal_progress.set(0)

        self.goal_hint = ctk.CTkLabel(
            self.goal_card,
            text="Cada sessao concluida empurra sua meta para frente.",
            font=("Segoe UI", 12),
            text_color=MUTED,
        )
        self.goal_hint.grid(row=2, column=0, sticky="w", padx=18, pady=(10, 16))

    def create_forest(self) -> None:
        self.side_panel = ctk.CTkFrame(
            self,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        self.side_panel.grid(row=4, column=2, sticky="nsew", padx=(8, 0), pady=(0, 16))
        self.side_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.side_panel,
            text="Floresta de foco",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))

        self.forest_caption = ctk.CTkLabel(
            self.side_panel,
            text="Plante sua primeira arvore.",
            font=("Segoe UI", 12),
            text_color=MUTED,
        )
        self.forest_caption.grid(row=1, column=0, sticky="w", padx=18)

        self.forest_grid = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.forest_grid.grid(row=2, column=0, sticky="ew", padx=18, pady=(12, 10))

        self.quick_stats = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.quick_stats.grid(row=3, column=0, sticky="ew", padx=18, pady=(4, 16))
        self.quick_stats.grid_columnconfigure(0, weight=1)
        self.quick_stats.grid_columnconfigure(1, weight=1)

        self.total_focus_card = StatCard(
            self.quick_stats,
            title="Foco total",
            value="0 min",
            subtitle="Historico acumulado",
            corner_radius=16,
        )
        self.total_focus_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.productivity_card = StatCard(
            self.quick_stats,
            title="Produtividade",
            value="0%",
            subtitle="Tasks concluidas",
            corner_radius=16,
        )
        self.productivity_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def refresh(self) -> None:
        self.snapshot = self.data_provider.load_snapshot()
        snapshot = self.snapshot

        self.welcome_label.configure(text=f"Bem-vindo de volta, {snapshot.user_name}")
        self.summary_label.configure(
            text=f"XP: {snapshot.xp} | Nivel {snapshot.level} - {snapshot.title} | {snapshot.streak} dias"
        )
        self.xp_progress.set(snapshot.xp_progress)
        self.xp_caption.configure(text=f"{snapshot.xp}/{snapshot.xp_goal} XP para o proximo nivel")
        self.streak_value.configure(text=f"{snapshot.streak} dias seguidos")
        self.streak_hint.configure(text=self._streak_hint(snapshot.streak))

        self.dynamic_message.configure(text=get_dynamic_message(snapshot))
        self.last_session_card.set_value(snapshot.last_session["duration"], icon="●")
        self.last_session_card.set_subtitle(
            f"{snapshot.last_session['task']} | {snapshot.last_session['time']}"
        )
        self.last_task_card.set_value(snapshot.last_task["name"])
        self.last_task_card.set_subtitle(
            f"{snapshot.last_task['progress']} | {snapshot.last_task['status']}"
        )
        self.course_card.set_value(snapshot.current_course["name"])
        self.course_card.set_subtitle(
            f"{snapshot.current_course['lesson']} | {snapshot.current_course['progress']}"
        )

        percent = int(snapshot.goal_progress * 100)
        self.goal_value.configure(text=f"{snapshot.today_sessions}/{snapshot.goal_target} sessoes")
        self.goal_percent.configure(text=f"{percent}%")
        self.goal_progress.set(snapshot.goal_progress)
        self.goal_hint.configure(text=self._goal_hint(snapshot.today_sessions, snapshot.goal_target))
        self.goal_progress.configure(progress_color=GREEN if percent < 100 else CYAN)
        self.goal_percent.configure(text_color=CYAN if percent >= 100 else GREEN)

        self.forest_caption.configure(text=snapshot.forest_message)
        self.total_focus_card.set_value(snapshot.focus_total)
        self.total_focus_card.set_subtitle(f"{snapshot.today_minutes} min hoje")
        self.productivity_card.set_value(snapshot.productivity)
        self.productivity_card.set_subtitle("Taxa de conclusao atual")

        self._render_forest(snapshot.forest)
        self._render_chart(
            host=self.focus_chart_card["host"],
            title="Minutos focados",
            values=[int(item["minutes"]) for item in snapshot.week_focus],
            labels=[str(item["label"]) for item in snapshot.week_focus],
            color=CYAN,
            kind="line",
        )
        self._render_chart(
            host=self.sessions_chart_card["host"],
            title="Sessoes",
            values=[int(item["value"]) for item in snapshot.sessions_by_day],
            labels=[str(item["label"]) for item in snapshot.sessions_by_day],
            color=ORANGE,
            kind="bar",
        )

    from typing import Dict

    def _chart_card(self, title: str) -> Dict[str, ctk.CTkFrame]:
        card = ctk.CTkFrame(
            self,
            fg_color=SURFACE_ALT,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))

        host = ctk.CTkFrame(card, fg_color=SURFACE_ALT)
        host.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        return {"card": card, "host": host}

    def _render_chart(
        self,
        host: ctk.CTkFrame,
        title: str,
        values: list[int],
        labels: list[str],
        color: str,
        kind: str,
    ) -> None:
        for child in host.winfo_children():
            child.destroy()
        self._chart_canvases = [canvas for canvas in self._chart_canvases if canvas.get_tk_widget().winfo_exists()]

        if Figure is None or FigureCanvasTkAgg is None:
            ctk.CTkLabel(
                host,
                text="matplotlib nao disponivel neste ambiente.",
                text_color=TEXT,
            ).pack(pady=20)
            return

        figure = Figure(figsize=(5.2, 2.4), dpi=100, facecolor=SURFACE_ALT)
        ax = figure.add_subplot(111)
        ax.set_facecolor(SURFACE_ALT)

        if values and any(value > 0 for value in values):
            if kind == "line":
                ax.plot(labels, values, color=color, linewidth=2.6, marker="o", markersize=6)
                ax.fill_between(labels, values, color=color, alpha=0.15)
            else:
                bars = ax.bar(labels, values, color=color, alpha=0.85)
                for bar in bars:
                    bar.set_linewidth(0)
        else:
            ax.text(
                0.5,
                0.5,
                "Sem dados ainda",
                ha="center",
                va="center",
                color=MUTED,
                fontsize=12,
                transform=ax.transAxes,
            )
            ax.set_xticks([])
            ax.set_yticks([])

        ax.set_title(title, color=MUTED, fontsize=11, loc="left", pad=10)
        ax.tick_params(axis="x", colors=MUTED, labelsize=10)
        ax.tick_params(axis="y", colors=MUTED, labelsize=9)
        ax.spines["bottom"].set_color(BORDER)
        ax.spines["left"].set_color(BORDER)
        ax.spines["top"].set_color(SURFACE_ALT)
        ax.spines["right"].set_color(SURFACE_ALT)
        ax.grid(axis="y", color="#1E293B", linewidth=0.8, alpha=0.8)

        canvas = FigureCanvasTkAgg(figure, master=host)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._chart_canvases.append(canvas)

    def _render_forest(self, forest: list[str]) -> None:
        for child in self.forest_grid.winfo_children():
            child.destroy()

        trees = forest[-8:] if forest else []
        if not trees:
            ctk.CTkLabel(
                self.forest_grid,
                text="Sem arvores por enquanto.",
                font=("Segoe UI", 12),
                text_color=MUTED,
            ).grid(row=0, column=0, sticky="w")
            return

        for index, tree in enumerate(trees):
            row = index // 4
            column = index % 4
            card = ctk.CTkFrame(self.forest_grid, fg_color="#0E1A16", corner_radius=14)
            card.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")
            ctk.CTkLabel(
                card,
                text=tree,
                font=("Segoe UI Emoji", 22),
                text_color=GREEN,
                width=36,
                height=36,
            ).pack(padx=8, pady=6)

    def _goal_hint(self, current: int, target: int) -> str:
        if current >= target:
            return "Meta concluida. Excelente consistencia."
        remaining = max(0, target - current)
        if remaining == 1:
            return "Falta 1 sessao para fechar sua meta."
        return f"Faltam {remaining} sessoes para completar o dia."

    def _streak_hint(self, streak: int) -> str:
        if streak <= 0:
            return "Comece hoje para abrir sua sequencia."
        if streak < 3:
            return "Sua consistencia ja comecou a aparecer."
        if streak < 7:
            return "Boa fase. Continue protegendo esse ritmo."
        return "Sequencia forte. Hoje vale ouro."

    def _animate_streak(self) -> None:
        if not hasattr(self, "_streak_color_index"):
            self._streak_color_index = 0

        self._streak_color_index = (self._streak_color_index + 1) % len(self._streak_colors)

        self.streak_value.configure(
            text_color=self._streak_colors[self._streak_color_index]
        )

        self.after(900, self._animate_streak)
    


class DashboardScreen(BaseScreen):
    title = "Dashboard"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content.grid_columnconfigure(0, weight=1)

        self.home = HomeUI(self.content, controller=controller)
        self.home.grid(row=0, column=0, sticky="nsew")

    def on_show(self) -> None:
        super().on_show()
        self.home.refresh()
