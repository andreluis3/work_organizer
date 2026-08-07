# frontend/pyqt_ui/viewmodels/dashboard_viewmodel.py
"""
ViewModel do Dashboard.

Ponte entre DashboardController (dados crus) e os widgets Qt (dados prontos
para exibir). Responsabilidade única: transformar o DashboardSnapshot em
DTOs de apresentação, um por seção da tela — sem SQL, sem regra de negócio,
sem widgets. Se uma pergunta for "qual é o fato?", a resposta mora no
DashboardService. Se for "como eu escrevo esse fato na tela?", mora aqui.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from backend.controllers.dashboard_controller import DashboardController
from backend.services.dashboard_service import DashboardSnapshot

FOREST_PREVIEW_SIZE = 8
"""Quantas árvores o Dashboard mostra. Regra de apresentação, não de domínio —
outras telas podem usar um número diferente sem o backend saber disso."""


# ----------------------------------------------------------------------
# DTOs de apresentação — um por widget, imutáveis
# ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class HeaderViewData:
    welcome_text: str
    summary_text: str
    xp_progress: float  # 0.0–1.0, pronto pro QProgressBar/anel
    xp_caption: str
    streak_value_text: str
    streak_hint_text: str


@dataclass(frozen=True, slots=True)
class HeroViewData:
    dynamic_message: str
    last_session_value: str
    last_session_subtitle: str
    last_task_value: str
    last_task_subtitle: str
    course_value: str
    course_subtitle: str


@dataclass(frozen=True, slots=True)
class GoalViewData:
    goal_label: str  # "3/5 sessões"
    goal_percent_text: str  # "60%"
    goal_progress: float  # 0.0–1.0
    goal_hint: str
    is_completed: bool  # widget decide a cor via QSS state, não o ViewModel


@dataclass(frozen=True, slots=True)
class ForestViewData:
    trees: list[str]  # já cortado nas últimas N árvores
    message: str
    total_focus_text: str  # "1h 30m"
    total_focus_subtitle: str
    productivity_text: str  # "72%"
    productivity_subtitle: str


@dataclass(frozen=True, slots=True)
class ChartsViewData:
    week_labels: list[str]
    week_minutes: list[int]
    week_sessions: list[int]


# ----------------------------------------------------------------------
# ViewModel
# ----------------------------------------------------------------------


class DashboardViewModel(QObject):
    """
    Emite `updated` sempre que um novo snapshot é processado. A DashboardPage
    escuta esse sinal e repassa `self.header`, `self.hero` etc. para os
    widgets correspondentes.
    """

    updated = pyqtSignal()

    def __init__(self, controller: DashboardController | None = None) -> None:
        super().__init__()
        self.controller = controller or DashboardController()

        self.header: HeaderViewData | None = None
        self.hero: HeroViewData | None = None
        self.goal: GoalViewData | None = None
        self.forest: ForestViewData | None = None
        self.charts: ChartsViewData | None = None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        snapshot = self.controller.get_snapshot()

        self.header = self._build_header(snapshot)
        self.hero = self._build_hero(snapshot)
        self.goal = self._build_goal(snapshot)
        self.forest = self._build_forest(snapshot)
        self.charts = self._build_charts(snapshot)

        self.updated.emit()

    # ------------------------------------------------------------------
    # Builders — um por seção/widget
    # ------------------------------------------------------------------

    def _build_header(self, snapshot: DashboardSnapshot) -> HeaderViewData:
        return HeaderViewData(
            welcome_text=f"Bem-vindo de volta, {snapshot.user_name}",
            summary_text=(
                f"XP: {snapshot.xp} | Nivel {snapshot.level} - "
                f"{snapshot.level_title} | {snapshot.streak} dias"
            ),
            xp_progress=snapshot.xp_progress,
            xp_caption=f"{snapshot.xp}/{snapshot.xp_goal} XP para o proximo nivel",
            streak_value_text=f"{snapshot.streak} dias seguidos",
            streak_hint_text=self._streak_hint_text(snapshot.streak),
        )

    def _build_hero(self, snapshot: DashboardSnapshot) -> HeroViewData:
        last_session_value = (
            f"{snapshot.last_session_duration_min} min"
            if snapshot.last_session_duration_min is not None
            else "--"
        )
        last_session_subtitle = (
            f"{snapshot.last_session_task_name or 'Sessao de foco'} | "
            f"{snapshot.last_session_time or '--:--'}"
            if snapshot.last_session_duration_min is not None
            else "Sem registro recente"
        )

        last_task_value = snapshot.last_task_name or "Nenhuma task recente"
        last_task_subtitle = (
            f"{snapshot.last_task_progress_label} | {snapshot.last_task_status_label}"
            if snapshot.last_task_name
            else "Sem progresso recente"
        )

        course_value = snapshot.current_course_name or "Nenhum curso em andamento"
        course_subtitle = (
            f"{snapshot.current_course_lesson} | {snapshot.current_course_progress_label}"
            if snapshot.current_course_name
            else "Adicione um curso para acompanhar."
        )

        return HeroViewData(
            dynamic_message=self.controller.get_dynamic_message(snapshot),
            last_session_value=last_session_value,
            last_session_subtitle=last_session_subtitle,
            last_task_value=last_task_value,
            last_task_subtitle=last_task_subtitle,
            course_value=course_value,
            course_subtitle=course_subtitle,
        )

    def _build_goal(self, snapshot: DashboardSnapshot) -> GoalViewData:
        percent = int(snapshot.goal_progress * 100)
        return GoalViewData(
            goal_label=f"{snapshot.goal_current}/{snapshot.goal_target} sessoes",
            goal_percent_text=f"{percent}%",
            goal_progress=snapshot.goal_progress,
            goal_hint=self._goal_hint_text(snapshot.goal_current, snapshot.goal_target),
            is_completed=percent >= 100,
        )

    def _build_forest(self, snapshot: DashboardSnapshot) -> ForestViewData:
        trees = snapshot.forest.trees[-FOREST_PREVIEW_SIZE:]
        return ForestViewData(
            trees=trees,
            message=snapshot.forest.message,
            total_focus_text=self._format_minutes(snapshot.total_minutes),
            total_focus_subtitle=f"{snapshot.today_minutes} min hoje",
            productivity_text=f"{snapshot.productivity_percent}%",
            productivity_subtitle="Taxa de conclusao atual",
        )

    def _build_charts(self, snapshot: DashboardSnapshot) -> ChartsViewData:
        return ChartsViewData(
            week_labels=[str(item["label"]) for item in snapshot.week_focus],
            week_minutes=[int(item["minutes"]) for item in snapshot.week_focus],
            week_sessions=[int(item["sessions"]) for item in snapshot.week_focus],
        )

    # ------------------------------------------------------------------
    # Formatadores privados (texto/número -> texto de apresentação)
    # ------------------------------------------------------------------

    def _format_minutes(self, minutes: int) -> str:
        hours, remainder = divmod(max(0, minutes), 60)
        if hours:
            return f"{hours}h {remainder:02d}m"
        return f"{remainder} min"

    def _streak_hint_text(self, streak: int) -> str:
        if streak <= 0:
            return "Comece hoje para abrir sua sequencia."
        if streak < 3:
            return "Sua consistencia ja comecou a aparecer."
        if streak < 7:
            return "Boa fase. Continue protegendo esse ritmo."
        return "Sequencia forte. Hoje vale ouro."

    def _goal_hint_text(self, current: int, target: int) -> str:
        if current >= target:
            return "Meta concluida. Excelente consistencia."
        remaining = max(0, target - current)
        if remaining == 1:
            return "Falta 1 sessao para fechar sua meta."
        return f"Faltam {remaining} sessoes para completar o dia."