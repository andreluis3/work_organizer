from __future__ import annotations

from backend.services.pomodoro_service import FocusViewState, PomodoroService


class PomodoroController:
    """Fachada fina entre a ViewModel e o PomodoroService."""

    def __init__(self, service: PomodoroService | None = None) -> None:
        self._service = service or PomodoroService()

    def toggle_primary_action(self, session_minutes: int | None = None) -> None:
        self._service.toggle_primary_action(session_minutes)

    def reset(self) -> None:
        self._service.reset()

    def tick(self) -> bool:
        return self._service.tick()

    def refresh_metrics(self) -> None:
        self._service.refresh_metrics()

    def get_view_state(self) -> FocusViewState:
        return self._service.get_view_state()
