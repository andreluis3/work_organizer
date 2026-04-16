from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Callable

from backend.database.conexao import conectar, registrar_sessao
from frontend.telas.forest_system import ForestSystem


@dataclass
class FocusMetrics:
    total_minutes: int = 0
    completed_sessions: int = 0
    month_sessions: int = 0


class FocusController:
    def __init__(self, app_controller, default_minutes: int = 25) -> None:
        self.app_controller = app_controller
        self.default_minutes = default_minutes
        self.state = "stopped"

        self.session_minutes = default_minutes
        self.total_seconds = default_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at: datetime | None = None

        self.metrics = FocusMetrics()
        self.forest_system = ForestSystem()

        self._after: Callable[[int, Callable], str] | None = None
        self._after_cancel: Callable[[str], None] | None = None
        self._job: str | None = None
        self._on_change: Callable[[dict], None] | None = None
        self._on_reset_input: Callable[[int], None] | None = None
        self._minutes_provider: Callable[[], str] | None = None

        self.refresh_from_history()

    def bind_scheduler(
        self,
        after_callback: Callable[[int, Callable], str],
        cancel_callback: Callable[[str], None],
    ) -> None:
        self._after = after_callback
        self._after_cancel = cancel_callback

    def bind_view(
        self,
        on_change: Callable[[dict], None],
        minutes_provider: Callable[[], str],
        on_reset_input: Callable[[int], None],
    ) -> None:
        self._on_change = on_change
        self._minutes_provider = minutes_provider
        self._on_reset_input = on_reset_input
        self._notify()

    def refresh_from_history(self) -> None:
        self.metrics = self._load_metrics()
        self.forest_system.load_count(self.metrics.month_sessions)
        self._notify()

    def handle_primary_action(self) -> None:
        if self.state == "running":
            self.pause_session()
            return
        if self.state == "paused":
            self.resume_session()
            return
        self.start_session()

    def start_session(self) -> None:
        self.session_minutes = self._read_session_minutes()
        self.total_seconds = self.session_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at = datetime.now()
        self.state = "running"
        self._schedule_next_tick()
        self._notify()

    def pause_session(self) -> None:
        if self.state != "running":
            return
        self.state = "paused"
        self._cancel_scheduled_tick()
        self._notify()

    def resume_session(self) -> None:
        if self.state != "paused":
            return
        self.state = "running"
        self._schedule_next_tick()
        self._notify()

    def reset_session(self) -> None:
        self._cancel_scheduled_tick()
        self.state = "stopped"
        self.session_minutes = self.default_minutes
        self.total_seconds = self.default_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_started_at = None
        if self._on_reset_input is not None:
            self._on_reset_input(self.default_minutes)
        self._notify()

    def destroy(self) -> None:
        self._cancel_scheduled_tick()

    def _schedule_next_tick(self) -> None:
        if self._after is None:
            return
        self._cancel_scheduled_tick()
        self._job = self._after(1000, self._tick)

    def _cancel_scheduled_tick(self) -> None:
        if self._job is None or self._after_cancel is None:
            self._job = None
            return
        try:
            self._after_cancel(self._job)
        except Exception:
            pass
        self._job = None

    def _tick(self) -> None:
        self._job = None
        if self.state != "running":
            return

        self.remaining_seconds = max(0, self.remaining_seconds - 1)
        if self.remaining_seconds == 0:
            self.finish_session()
            return

        self._notify()
        self._schedule_next_tick()

    def finish_session(self) -> None:
        self._cancel_scheduled_tick()
        self.state = "stopped"

        finished_at = datetime.now()
        if self.session_started_at is not None:
            try:
                expected_end = self.session_started_at + timedelta(seconds=self.total_seconds)
                registrar_sessao(
                    tarefa_id=1,
                    inicio=self.session_started_at,
                    fim=max(finished_at, expected_end),
                    observacao="Focus session completa",
                )
            except Exception:
                pass

        self.forest_system.add_tree()
        self.metrics = self._load_metrics()
        self.metrics.month_sessions = max(
            self.metrics.month_sessions,
            len(self.forest_system.get_forest()),
        )

        self.remaining_seconds = self.total_seconds
        self.session_started_at = None
        self._notify()

        if hasattr(self.app_controller, "toast"):
            self.app_controller.toast("Sessão concluída. Sua floresta ganhou uma nova árvore.", level="success")

    def get_view_model(self) -> dict:
        elapsed_seconds = self.total_seconds - self.remaining_seconds
        progress = 0 if self.total_seconds <= 0 else elapsed_seconds / self.total_seconds

        sessions_for_level = 4
        level = max(1, (self.metrics.completed_sessions // sessions_for_level) + 1)
        level_xp = self.metrics.completed_sessions % sessions_for_level
        xp_progress = level_xp / sessions_for_level

        hours, minutes = divmod(self.metrics.total_minutes, 60)
        total_focused = f"{hours}h {minutes:02d}m" if hours else f"{minutes} min"

        mm, ss = divmod(self.remaining_seconds, 60)
        return {
            "state": self.state,
            "timer_text": f"{mm:02d}:{ss:02d}",
            "primary_label": self._primary_button_text(),
            "progress": progress,
            "xp_progress": xp_progress,
            "xp_text": f"XP {int(xp_progress * 100)}/100",
            "level_text": f"Foco Nível {level} - Deep Work",
            "total_focused": total_focused,
            "completed_sessions": str(self.metrics.completed_sessions),
            "forest": self.forest_system.get_forest(),
            "forest_message": self.forest_system.get_message(),
            "is_running": self.state == "running",
            "session_minutes": str(self.session_minutes),
        }

    def _notify(self) -> None:
        if self._on_change is not None:
            self._on_change(self.get_view_model())

    def _primary_button_text(self) -> str:
        if self.state == "running":
            return "Pause"
        if self.state == "paused":
            return "Resume"
        return "Start"

    def _read_session_minutes(self) -> int:
        if self._minutes_provider is None:
            return self.default_minutes

        raw_value = str(self._minutes_provider()).strip()
        try:
            minutes = int(raw_value)
        except (TypeError, ValueError):
            minutes = self.default_minutes
        return minutes if minutes > 0 else self.default_minutes

    def _load_metrics(self) -> FocusMetrics:
        metrics = FocusMetrics()
        month_prefix = date.today().strftime("%Y-%m")

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0), COUNT(*)
                FROM pomodoro
                """
            )
            total_row = cursor.fetchone() or (0, 0)
            metrics.total_minutes = int(total_row[0] or 0)
            metrics.completed_sessions = int(total_row[1] or 0)

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM pomodoro
                WHERE substr(inicio, 1, 7) = ?
                """,
                (month_prefix,),
            )
            month_row = cursor.fetchone() or (0,)
            metrics.month_sessions = int(month_row[0] or 0)

            conn.close()
        except Exception:
            pass

        return metrics
