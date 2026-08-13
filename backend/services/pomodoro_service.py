from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum

from backend.database.pomodoro_repository import PomodoroRepository

DEFAULT_SESSION_MINUTES = 25

# TODO(andré): tarefa_id fixo em 1, espelhando o comportamento legado.
# Quando a integração real com Tasks for definida, trocar por um tarefa_id
# selecionado pelo usuário (requer confirmação antes de mudar essa regra).
DEFAULT_TAREFA_ID = 1

SESSIONS_PER_LEVEL = 4


class FocusState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class FocusMetrics:
    total_minutes: int = 0
    completed_sessions: int = 0
    month_sessions: int = 0


@dataclass
class FocusViewState:
    """Snapshot pronto para a ViewModel traduzir em DTOs de apresentação."""

    state: FocusState
    remaining_seconds: int
    total_seconds: int
    session_minutes: int
    metrics: FocusMetrics
    forest_count: int

    @property
    def is_running(self) -> bool:
        return self.state is FocusState.RUNNING

    @property
    def is_paused(self) -> bool:
        return self.state is FocusState.PAUSED

    @property
    def progress(self) -> float:
        if self.total_seconds <= 0:
            return 0.0
        elapsed = self.total_seconds - self.remaining_seconds
        return elapsed / self.total_seconds

    @property
    def timer_text(self) -> str:
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def primary_label(self) -> str:
        return {
            FocusState.RUNNING: "Pause",
            FocusState.PAUSED: "Resume",
        }.get(self.state, "Start")

    @property
    def total_focused_text(self) -> str:
        hours, minutes = divmod(self.metrics.total_minutes, 60)
        return f"{hours}h {minutes:02d}m" if hours else f"{minutes} min"

    @property
    def level(self) -> int:
        return max(1, (self.metrics.completed_sessions // SESSIONS_PER_LEVEL) + 1)

    @property
    def xp_progress(self) -> float:
        return (self.metrics.completed_sessions % SESSIONS_PER_LEVEL) / SESSIONS_PER_LEVEL

    @property
    def level_text(self) -> str:
        return f"Foco Nível {self.level} - Deep Work"

    @property
    def xp_text(self) -> str:
        return f"XP {int(self.xp_progress * 100)}/100"

    @property
    def forest_message(self) -> str:
        if self.forest_count == 0:
            return "Plante sua primeira árvore."
        if self.forest_count < 3:
            return "Sua floresta está começando..."
        if self.forest_count < 10:
            return "Sua floresta está crescendo"
        return "Sua floresta está prosperando"


class PomodoroService:
    """Regra de negócio pura do Focus Time. Sem SQL direto, sem Qt."""

    def __init__(self, repository: PomodoroRepository | None = None) -> None:
        self._repository = repository or PomodoroRepository()

        self.state = FocusState.STOPPED
        self.session_minutes = DEFAULT_SESSION_MINUTES
        self.total_seconds = self.session_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at: datetime | None = None

        self.metrics = FocusMetrics()
        self.forest_count = 0

        self.refresh_metrics()

    # ---- controle de sessão ----

    def start(self, session_minutes: int | None = None) -> None:
        self.session_minutes = self._sanitize_minutes(session_minutes)
        self.total_seconds = self.session_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at = datetime.now()
        self.state = FocusState.RUNNING

    def pause(self) -> None:
        if self.state is not FocusState.RUNNING:
            return
        self.state = FocusState.PAUSED

    def resume(self) -> None:
        if self.state is not FocusState.PAUSED:
            return
        self.state = FocusState.RUNNING

    def reset(self) -> None:
        self.state = FocusState.STOPPED
        self.session_minutes = DEFAULT_SESSION_MINUTES
        self.total_seconds = self.session_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at = None

    def toggle_primary_action(self, session_minutes: int | None = None) -> None:
        if self.state is FocusState.RUNNING:
            self.pause()
        elif self.state is FocusState.PAUSED:
            self.resume()
        else:
            self.start(session_minutes)

    def tick(self) -> bool:
        """Avança 1 segundo. Retorna True se a sessão foi concluída neste tick."""
        if self.state is not FocusState.RUNNING:
            return False

        self.remaining_seconds = max(0, self.remaining_seconds - 1)
        if self.remaining_seconds == 0:
            self._finish_session()
            return True
        return False

    def _finish_session(self) -> None:
        self.state = FocusState.STOPPED
        finished_at = datetime.now()

        if self.session_started_at is not None:
            expected_end = self.session_started_at + timedelta(seconds=self.total_seconds)
            fim = max(finished_at, expected_end)
            duracao_min = int((fim - self.session_started_at).total_seconds() / 60)
            try:
                self._repository.registrar_sessao(
                    tarefa_id=DEFAULT_TAREFA_ID,
                    inicio=self.session_started_at,
                    fim=fim,
                    duracao_min=duracao_min,
                    observacao="Focus session completa",
                )
            except Exception:
                pass

        self.refresh_metrics()

        self.remaining_seconds = self.total_seconds
        self.session_started_at = None

    # ---- métricas ----

    def refresh_metrics(self) -> None:
        total_minutes, completed_sessions = self._repository.obter_totais()
        month_sessions = self._repository.contar_sessoes_do_mes(date.today())

        self.metrics = FocusMetrics(
            total_minutes=total_minutes,
            completed_sessions=completed_sessions,
            month_sessions=month_sessions,
        )
        self.forest_count = month_sessions

    # ---- snapshot para a UI ----

    def get_view_state(self) -> FocusViewState:
        return FocusViewState(
            state=self.state,
            remaining_seconds=self.remaining_seconds,
            total_seconds=self.total_seconds,
            session_minutes=self.session_minutes,
            metrics=self.metrics,
            forest_count=self.forest_count,
        )

    @staticmethod
    def _sanitize_minutes(value: int | None) -> int:
        if value is None or value <= 0:
            return DEFAULT_SESSION_MINUTES
        return value
