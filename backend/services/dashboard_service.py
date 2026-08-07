# backend/services/dashboard_service.py
"""
Serviço de agregação do Dashboard.

Responsabilidade única: montar o DashboardSnapshot combinando
DashboardRepository (dados brutos), ForestService (floresta) e
TaskService (última task/curso/produtividade). Nenhuma SQL direta aqui,
nenhuma UI. Migração das regras de negócio que estavam soltas dentro do
antigo DashboardDataProvider (frontend/telas/dashboard.py).
"""

from __future__ import annotations

import getpass
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from backend.database.dashboard_repository import DashboardRepository
from backend.services.forest_service import ForestService, ForestSnapshot
from backend.services.task_service import TaskService

LEVEL_TITLES = [
    "Deep Worker",
    "Momentum Builder",
    "Focus Ranger",
    "Flow Architect",
    "Master of Consistency",
]

SESSIONS_PER_LEVEL = 4
XP_GOAL = 100
DEFAULT_GOAL_TARGET = 5


@dataclass(slots=True)
class DashboardSnapshot:
    user_name: str

    xp: int
    xp_goal: int
    level: int
    level_title: str

    streak: int

    today_sessions: int
    today_minutes: int

    goal_target: int
    goal_current: int

    total_minutes: int
    total_sessions: int
    productivity_percent: int

    last_session_duration_min: int | None
    last_session_task_name: str | None
    last_session_time: str | None

    last_task_name: str | None
    last_task_progress_label: str | None
    last_task_status_label: str | None

    current_course_name: str | None
    current_course_lesson: str | None
    current_course_progress_label: str | None

    forest: ForestSnapshot

    week_focus: list[dict] = field(default_factory=list)
    """[{"label": "Seg", "minutes": 30, "sessions": 2}, ...] — 7 dias."""

    task_focus: list[dict] = field(default_factory=list)
    """[{"label": "Relatório X", "minutes": 120}, ...] — top tasks por foco."""

    @property
    def xp_progress(self) -> float:
        return self.xp / self.xp_goal if self.xp_goal else 0.0

    @property
    def goal_progress(self) -> float:
        if not self.goal_target:
            return 0.0
        return min(1.0, self.goal_current / self.goal_target)


class DashboardService:
    def __init__(
        self,
        repository: DashboardRepository | None = None,
        forest_service: ForestService | None = None,
        task_service: TaskService | None = None,
    ) -> None:
        self.repository = repository or DashboardRepository()
        self.forest_service = forest_service or ForestService()
        self.task_service = task_service or TaskService()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def get_snapshot(self) -> DashboardSnapshot:
        today_minutes, today_sessions = self.repository.get_today_sessions()
        total_minutes, total_sessions = self.repository.get_totals()
        week_focus = self.repository.get_week_sessions()

        level = self._compute_level(total_sessions)
        xp = self._compute_xp(total_sessions)

        last_session = self._build_last_session(self.repository.get_last_session())
        last_task_name, last_task_progress, last_task_status = self._build_last_task()
        course_name, course_lesson, course_progress = self._build_current_course()

        return DashboardSnapshot(
            user_name=self._get_user_name(),
            xp=xp,
            xp_goal=XP_GOAL,
            level=level,
            level_title=self._resolve_level_title(level),
            streak=self._compute_streak(),
            today_sessions=today_sessions,
            today_minutes=today_minutes,
            goal_target=self._resolve_goal_target(),
            goal_current=today_sessions,
            total_minutes=total_minutes,
            total_sessions=total_sessions,
            productivity_percent=self._compute_productivity(),
            last_session_duration_min=last_session[0],
            last_session_task_name=last_session[1],
            last_session_time=last_session[2],
            last_task_name=last_task_name,
            last_task_progress_label=last_task_progress,
            last_task_status_label=last_task_status,
            current_course_name=course_name,
            current_course_lesson=course_lesson,
            current_course_progress_label=course_progress,
            forest=self.forest_service.build(total_sessions),
            week_focus=week_focus,
            task_focus=self._build_task_focus(),
        )

    def get_dynamic_message(self, snapshot: DashboardSnapshot) -> str:
        """Mensagem motivacional baseada no progresso da meta diária."""
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

    # ------------------------------------------------------------------
    # XP / Nível / Streak
    # ------------------------------------------------------------------

    def _compute_xp(self, total_sessions: int) -> int:
        return int((total_sessions % SESSIONS_PER_LEVEL) * (XP_GOAL / SESSIONS_PER_LEVEL))

    def _compute_level(self, total_sessions: int) -> int:
        return max(1, (total_sessions // SESSIONS_PER_LEVEL) + 1)

    def _resolve_level_title(self, level: int) -> str:
        index = min(len(LEVEL_TITLES) - 1, max(0, level - 1))
        return LEVEL_TITLES[index]

    def _compute_streak(self) -> int:
        day_strings = self.repository.get_session_days()
        if not day_strings:
            return 0

        days = {
            datetime.strptime(value, "%Y-%m-%d").date()
            for value in day_strings
        }

        streak = 0
        current = date.today()

        if current not in days and (current - timedelta(days=1)) in days:
            current -= timedelta(days=1)

        while current in days:
            streak += 1
            current -= timedelta(days=1)

        return streak

    # ------------------------------------------------------------------
    # Meta diária
    # ------------------------------------------------------------------

    def _resolve_goal_target(self) -> int:
        target = self.repository.get_active_goal_target()
        return target if target and target > 0 else DEFAULT_GOAL_TARGET

    # ------------------------------------------------------------------
    # Última sessão
    # ------------------------------------------------------------------

    def _build_last_session(self, row: dict | None) -> tuple[int | None, str | None, str | None]:
        if not row:
            return None, None, None

        duration = int(row.get("duracao_min") or 0)
        task_name = self.repository.resolve_task_name(row.get("tarefa_id"))
        if not task_name:
            task_name = row.get("observacao") or "Sessao de foco"

        time_value = row.get("fim") or row.get("inicio")
        time_label = self._format_clock(time_value)

        return duration, task_name, time_label

    # ------------------------------------------------------------------
    # Última task / curso (via TaskService, não SQL solto)
    # ------------------------------------------------------------------

    def _build_last_task(self) -> tuple[str | None, str | None, str | None]:
        tasks = [task for task in self.task_service.list_tasks() if task.get("type") != "course"]
        if not tasks:
            return None, None, None

        latest = sorted(
            tasks,
            key=lambda item: item.get("updated_at") or item.get("created_at") or "",
            reverse=True,
        )[0]

        progress = self._task_progress_label(latest)
        status = self._format_task_status(latest.get("status"))
        return latest.get("title", "Task recente"), progress, status

    def _build_current_course(self) -> tuple[str | None, str | None, str | None]:
        courses = [task for task in self.task_service.list_tasks() if task.get("type") == "course"]
        if not courses:
            return None, None, None

        latest = sorted(
            courses,
            key=lambda item: item.get("updated_at") or item.get("created_at") or "",
            reverse=True,
        )[0]

        course = latest.get("course") or {}
        progress = int(course.get("progress", 0) or 0)
        lesson = course.get("current_lesson") or "Aula 1"
        total = int(course.get("total_lessons", 0) or 0)

        progress_label = f"{progress}%"
        if total > 0:
            completed = int(round((progress / 100) * total))
            progress_label = f"{completed}/{total} aulas"

        return latest.get("title", "Curso atual"), lesson, progress_label

    def _task_progress_label(self, task: dict) -> str:
        subtasks = task.get("subtasks") or []
        if not subtasks:
            return self._format_task_status(task.get("status"))

        completed = sum(1 for item in subtasks if item.get("completed"))
        total = len(subtasks)
        return f"{int((completed / total) * 100) if total else 0}%"

    # ------------------------------------------------------------------
    # Produtividade (com fallback pra tabela legada)
    # ------------------------------------------------------------------

    def _compute_productivity(self) -> int:
        tasks = self.task_service.list_tasks()
        if tasks:
            completed = sum(1 for task in tasks if task.get("status") == "concluida")
            total = len(tasks)
            return int((completed / total) * 100) if total else 0

        total, completed = self.repository.get_legacy_task_counts()
        return int((completed / total) * 100) if total else 0

    # ------------------------------------------------------------------
    # Foco por task (top N)
    # ------------------------------------------------------------------

    def _build_task_focus(self) -> list[dict]:
        rows = self.repository.get_task_focus_totals(limit=4)
        result: list[dict] = []
        for row in rows:
            name = self.repository.resolve_task_name(row.get("tarefa_id")) or "Sem task"
            result.append({"label": name, "minutes": int(row.get("minutes") or 0)})
        return result

    # ------------------------------------------------------------------
    # Helpers de apresentação mínima (não-Qt, reaproveitável por qualquer UI)
    # ------------------------------------------------------------------

    def _get_user_name(self) -> str:
        raw_name = getpass.getuser().replace("_", " ").strip()
        return raw_name.title() if raw_name else "Usuario"

    def _format_clock(self, value: str | None) -> str | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value)).strftime("%H:%M")
        except ValueError:
            return str(value)[11:16] if len(str(value)) >= 16 else None

    def _format_task_status(self, status: str | None) -> str:
        mapping = {
            "done": "Concluida",
            "in_progress": "Em progresso",
            "pending": "Pendente",
            "concluida": "Concluida",
            "pendente": "Pendente",
        }
        return mapping.get(str(status or "").lower(), "Sem status")