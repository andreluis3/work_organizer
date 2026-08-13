from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from backend.controllers.pomodoro_controller import PomodoroController
from backend.services.pomodoro_service import FocusViewState


class FocusViewModel(QObject):
    """Traduz o estado do PomodoroController em snapshots prontos para a Page.

    Nenhuma regra de negócio nova aqui — só formatação/estado de UI (o QTimer
    que dirige o loop de 1s) e repasse do que o Controller já calculou.
    """

    view_state_changed = pyqtSignal(object)  # FocusViewState
    session_completed = pyqtSignal()

    def __init__(self, controller: PomodoroController | None = None, parent=None) -> None:
        super().__init__(parent)
        self._controller = controller or PomodoroController()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        self.session_minutes = self._controller.get_view_state().session_minutes

    def get_current_state(self) -> FocusViewState:
        """Snapshot atual, sem disparar o signal — útil para sincronizar a UI
        antes do primeiro on_show() (ex: montagem inicial do layout)."""
        return self._controller.get_view_state()

    def load(self) -> None:
        """Chamado no on_show() da Page — atualiza métricas vindas do banco."""
        self._controller.refresh_metrics()
        self._emit_state()

    def handle_primary_action(self, session_minutes: int | None = None) -> None:
        self._controller.toggle_primary_action(session_minutes)
        state = self._controller.get_view_state()

        if state.is_running:
            self._timer.start()
        else:
            self._timer.stop()

        self._emit_state(state)

    def reset_session(self) -> None:
        self._timer.stop()
        self._controller.reset()
        self._emit_state()

    def destroy(self) -> None:
        self._timer.stop()

    def _on_tick(self) -> None:
        completed = self._controller.tick()
        self._emit_state()
        if completed:
            self._timer.stop()
            self.session_completed.emit()

    def _emit_state(self, state: FocusViewState | None = None) -> None:
        state = state or self._controller.get_view_state()
        self.session_minutes = state.session_minutes
        self.view_state_changed.emit(state)