from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.viewmodels.focus_viewmodel import FocusViewModel
from frontend.pyqt_ui.widgets.focus.forest_panel_widget import ForestPanelWidget
from frontend.pyqt_ui.widgets.focus.metrics_panel_widget import MetricsPanelWidget
from frontend.pyqt_ui.widgets.focus.timer_ring_widget import TimerRingWidget


class FocusPage(BasePage):
    """Página do Focus Time / Pomodoro.

    Só monta layout e conecta sinais. Nenhuma regra de negócio, nenhum SQL —
    tudo isso vive em FocusViewModel -> PomodoroController -> PomodoroService.

    Segue o contrato do BasePage: NÃO sobrescreve `_build_layout()` (que já
    monta header + `self.content`/`self.content_layout`). Os widgets da
    feature entram via `add_content_widget()`, como o BasePage documenta.
    """

    title = "Focus"

    def __init__(self, parent: QWidget | None = None) -> None:
        # self.view_model precisa existir antes de _build_focus_layout() rodar.
        self.view_model = FocusViewModel()
        self.view_model.view_state_changed.connect(self._on_view_state_changed)
        self.view_model.session_completed.connect(self._on_session_completed)

        super().__init__(parent)  # monta self.content / self.content_layout e a intro animation
        self.setObjectName("focusPage")
        self.view_model.setParent(self)

        self._build_focus_layout()

    def on_show(self) -> None:
        super().on_show()  # mantém a animação de entrada do BasePage
        self.view_model.load()

    def stop_timer(self) -> None:
        """Chamar ao trocar de página / fechar o app, se a MainWindow expuser esse hook."""
        self.view_model.destroy()

    # ---- layout ----

    def _build_focus_layout(self) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(16)

        self._metrics_panel = MetricsPanelWidget()
        row_layout.addWidget(self._metrics_panel, 2)

        row_layout.addWidget(self._build_center_panel(), 6)

        self._forest_panel = ForestPanelWidget()
        row_layout.addWidget(self._forest_panel, 2)

        self.add_content_widget(row)

        # Sincroniza a UI com o estado inicial da ViewModel antes do primeiro on_show().
        self._on_view_state_changed(self.view_model.get_current_state())

    def _build_center_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("focusCenterPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        mode_label = QLabel("FOCUS MODE")
        mode_label.setObjectName("focusModeLabel")
        mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mode_label)

        self._timer_ring = TimerRingWidget()
        layout.addWidget(self._timer_ring, alignment=Qt.AlignmentFlag.AlignCenter)

        self._level_label = QLabel("Foco Nível 1 - Deep Work")
        self._level_label.setObjectName("levelLabel")
        self._level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._level_label)

        self._xp_bar = QProgressBar()
        self._xp_bar.setObjectName("xpBar")
        self._xp_bar.setRange(0, 100)
        self._xp_bar.setTextVisible(False)
        self._xp_bar.setFixedWidth(320)
        layout.addWidget(self._xp_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._xp_label = QLabel("XP 0/100")
        self._xp_label.setObjectName("xpLabel")
        self._xp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._xp_label)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        minutes_caption = QLabel("Sessão (min)")
        minutes_caption.setObjectName("minutesCaption")
        input_row.addWidget(minutes_caption)

        self._minutes_input = QLineEdit(str(self.view_model.session_minutes))
        self._minutes_input.setObjectName("minutesInput")
        self._minutes_input.setFixedWidth(80)
        self._minutes_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_row.addWidget(self._minutes_input)

        layout.addLayout(input_row)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._primary_button = QPushButton("Start")
        self._primary_button.setObjectName("primaryButton")
        self._primary_button.clicked.connect(self._on_primary_clicked)
        button_row.addWidget(self._primary_button)

        self._reset_button = QPushButton("Reset")
        self._reset_button.setObjectName("resetButton")
        self._reset_button.clicked.connect(self._on_reset_clicked)
        button_row.addWidget(self._reset_button)

        layout.addLayout(button_row)

        return panel

    # ---- eventos de UI ----

    def _on_primary_clicked(self) -> None:
        self.view_model.handle_primary_action(self._read_minutes())

    def _on_reset_clicked(self) -> None:
        self.view_model.reset_session()

    def _on_session_completed(self) -> None:
        # Espaço reservado para toast/notificação na conclusão da sessão.
        # Não sei ainda como o toast está exposto no seu AppState/MainWindow
        # novo — me avisa se quiser que eu conecte isso.
        pass

    # ---- reação ao estado da ViewModel ----

    def _on_view_state_changed(self, state) -> None:
        self._timer_ring.update_data(
            timer_text=state.timer_text,
            progress=state.progress,
            is_running=state.is_running,
            is_paused=state.is_paused,
        )
        self._level_label.setText(state.level_text)
        self._xp_bar.setValue(int(state.xp_progress * 100))
        self._xp_label.setText(state.xp_text)
        self._primary_button.setText(state.primary_label)

        self._metrics_panel.update_data(
            total_focused=state.total_focused_text,
            completed_sessions=str(state.metrics.completed_sessions),
            is_running=state.is_running,
        )
        self._forest_panel.update_data(state.forest_count, state.forest_message)

        is_stopped = not state.is_running and not state.is_paused
        if is_stopped:
            self._minutes_input.setText(str(state.session_minutes))
        self._minutes_input.setEnabled(is_stopped)

    def _read_minutes(self) -> int | None:
        raw_value = self._minutes_input.text().strip()
        try:
            minutes = int(raw_value)
        except ValueError:
            return None
        return minutes if minutes > 0 else None