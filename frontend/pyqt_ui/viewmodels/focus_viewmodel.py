from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from backend.controllers.pomodoro_controller import PomodoroController
from backend.services.audio_manager import AudioManager
from backend.services.pomodoro_service import FocusState, FocusViewState
from frontend.pyqt_ui.viewmodels.pomodoro_manager import PomodoroManager, PomodoroSnapshot


class FocusViewModel(QObject):
    """Traduz o estado do PomodoroController em snapshots prontos para a Page.

    Responsabilidades desta classe:
    - receber ações da interface (handle_primary_action, reset_session, etc.)
    - controlar o loop de 1s (QTimer) e o modo Pomodoro (PomodoroManager)
    - disparar os efeitos sonoros de acordo com a transição de estado
    - repassar o que o Controller/Service já calcularam

    Nenhuma regra de negócio de domínio nova aqui, e nenhum código PyQt de
    widget — só QObject/QTimer, que são a "cola" de UI já usada antes.
    """

    view_state_changed = pyqtSignal(object)      # FocusViewState
    session_completed = pyqtSignal()
    pomodoro_state_changed = pyqtSignal(object)  # PomodoroSnapshot
    pomodoro_completed = pyqtSignal()            # todos os ciclos do pomodoro terminaram

    def __init__(self, controller: PomodoroController | None = None, parent=None) -> None:
        super().__init__(parent)
        self._controller = controller or PomodoroController()
        self._audio = AudioManager()
        self._pomodoro = PomodoroManager()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        self.session_minutes = self._controller.get_view_state().session_minutes

    # ---- snapshots ----

    def get_current_state(self) -> FocusViewState:
        """Snapshot atual, sem disparar o signal — útil para sincronizar a UI
        antes do primeiro on_show() (ex: montagem inicial do layout)."""
        return self._controller.get_view_state()

    def get_pomodoro_state(self) -> PomodoroSnapshot:
        return self._pomodoro.get_snapshot()

    # ---- ciclo de vida ----

    def load(self) -> None:
        """Chamado no on_show() da Page — atualiza métricas vindas do banco."""
        self._controller.refresh_metrics()
        self._emit_state()

    def destroy(self) -> None:
        self._timer.stop()
        self._audio.stop_all()

    # ---- ações da UI: timer ----

    def handle_primary_action(self, session_minutes: int | None = None) -> None:
        previous_state = self._controller.get_view_state().state

        minutes = session_minutes
        if previous_state is FocusState.STOPPED and self._pomodoro.enabled:
            # No modo Pomodoro, quem manda no tempo é a fase atual, não o
            # QLineEdit de minutos (que fica desabilitado nesse modo).
            minutes = self._pomodoro.get_snapshot().session_minutes_for_phase

        self._controller.toggle_primary_action(minutes)
        state = self._controller.get_view_state()

        self._play_transition_sound(previous_state, state.state)

        if state.is_running:
            self._timer.start()
        else:
            self._timer.stop()

        self._emit_state(state)

    def reset_session(self) -> None:
        self._timer.stop()
        self._controller.reset()
        self._pomodoro.reset()
        self._audio.play_reset_sound()
        self._emit_state()
        self._emit_pomodoro_state()

    def _on_tick(self) -> None:
        completed = self._controller.tick()
        self._emit_state()

        if not completed:
            return

        self._timer.stop()
        self._audio.play_finish_sound()
        self.session_completed.emit()

        if not self._pomodoro.enabled:
            return

        pomodoro_finished = self._pomodoro.advance()
        self._emit_pomodoro_state()

        if pomodoro_finished:
            # Todos os ciclos concluídos: registrar sessão / futura integração
            # com XP acontece aqui (o "registro" básico já é feito pelo
            # PomodoroService a cada sessão via repositório).
            self.pomodoro_completed.emit()
            return

        # Avança automaticamente para a próxima fase (foco <-> pausa).
        next_minutes = self._pomodoro.get_snapshot().session_minutes_for_phase
        self._controller.toggle_primary_action(next_minutes)
        self._audio.play_start_sound()
        self._timer.start()
        self._emit_state()

    # ---- ações da UI: pomodoro ----

    def set_pomodoro_enabled(self, enabled: bool) -> None:
        if enabled:
            self._pomodoro.enable()
        else:
            self._pomodoro.disable()
        self._emit_pomodoro_state()

    def update_pomodoro_config(self, focus_minutes: int, break_minutes: int, total_cycles: int) -> None:
        self._pomodoro.update_config(focus_minutes, break_minutes, total_cycles)
        self._emit_pomodoro_state()

    # ---- som ----

    def _play_transition_sound(self, previous: FocusState, current: FocusState) -> None:
        if previous is FocusState.STOPPED and current is FocusState.RUNNING:
            self._audio.play_start_sound()
        elif previous is FocusState.RUNNING and current is FocusState.PAUSED:
            self._audio.play_pause_sound()
        elif previous is FocusState.PAUSED and current is FocusState.RUNNING:
            self._audio.play_resume_sound()

    # ---- emissão de estado ----

    def _emit_state(self, state: FocusViewState | None = None) -> None:
        state = state or self._controller.get_view_state()
        self.session_minutes = state.session_minutes
        self.view_state_changed.emit(state)

    def _emit_pomodoro_state(self) -> None:
        self.pomodoro_state_changed.emit(self._pomodoro.get_snapshot())