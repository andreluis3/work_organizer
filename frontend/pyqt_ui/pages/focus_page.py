from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
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
    tudo isso vive em FocusViewModel -> PomodoroController -> PomodoroService
    (e, para o modo Pomodoro, em PomodoroManager, que a ViewModel orquestra).

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
        self.view_model.pomodoro_state_changed.connect(self._on_pomodoro_state_changed)

        super().__init__(parent)  # monta self.content / self.content_layout e a intro animation
        self.setObjectName("focusPage")
        self.setFont(QFont("Segoe UI"))
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
        self._on_pomodoro_state_changed(self.view_model.get_pomodoro_state())

    def _build_center_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("focusCenterPanel")

        outer_layout = QHBoxLayout(panel)
        outer_layout.setContentsMargins(24, 28, 24, 28)
        outer_layout.setSpacing(20)

        outer_layout.addWidget(self._build_pomodoro_settings_box())
        outer_layout.addLayout(self._build_focus_column())

        return panel

    def _build_pomodoro_settings_box(self) -> QFrame:
        box = QFrame()
        box.setObjectName("settingsBox")
        box.setFixedWidth(210)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(12)

        self._pomodoro_checkbox = QCheckBox("Ativar modo Pomodoro")
        self._pomodoro_checkbox.setObjectName("pomodoroCheckbox")
        self._pomodoro_checkbox.stateChanged.connect(self._on_pomodoro_toggled)
        layout.addWidget(self._pomodoro_checkbox)

        self._pomodoro_fields_widget = QWidget()
        fields_layout = QVBoxLayout(self._pomodoro_fields_widget)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(10)

        self._focus_spin = self._build_pomodoro_spin(fields_layout, "Tempo de foco (min)", default=25, minimum=1, maximum=180)
        self._break_spin = self._build_pomodoro_spin(fields_layout, "Tempo de pausa (min)", default=5, minimum=1, maximum=60)
        self._cycles_spin = self._build_pomodoro_spin(fields_layout, "Quantidade de ciclos", default=4, minimum=1, maximum=20)

        for spin in (self._focus_spin, self._break_spin, self._cycles_spin):
            spin.valueChanged.connect(self._on_pomodoro_config_changed)

        layout.addWidget(self._pomodoro_fields_widget)
        self._pomodoro_fields_widget.setVisible(False)

        self._phase_label = QLabel("")
        self._phase_label.setObjectName("phaseLabel")
        self._phase_label.setWordWrap(True)
        layout.addWidget(self._phase_label)

        layout.addStretch()
        return box

    def _build_pomodoro_spin(
        self,
        parent_layout: QVBoxLayout,
        caption: str,
        default: int,
        minimum: int,
        maximum: int,
    ) -> QSpinBox:
        caption_label = QLabel(caption)
        caption_label.setObjectName("pomodoroFieldCaption")
        parent_layout.addWidget(caption_label)

        spin = QSpinBox()
        spin.setObjectName("pomodoroSpin")
        spin.setRange(minimum, maximum)
        spin.setValue(default)
        parent_layout.addWidget(spin)
        return spin

    def _build_focus_column(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
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

        return layout

    # ---- eventos de UI: timer ----

    def _on_primary_clicked(self) -> None:
        self.view_model.handle_primary_action(self._read_minutes())

    def _on_reset_clicked(self) -> None:
        self.view_model.reset_session()

    def _on_session_completed(self) -> None:
        # Espaço reservado para toast/notificação na conclusão da sessão.
        # Não sei ainda como o toast está exposto no seu AppState/MainWindow
        # novo — me avisa se quiser que eu conecte isso.
        pass

    # ---- eventos de UI: pomodoro ----

    def _on_pomodoro_toggled(self, checked_state: int) -> None:
        enabled = checked_state == Qt.CheckState.Checked.value
        self._pomodoro_fields_widget.setVisible(enabled)
        self.view_model.set_pomodoro_enabled(enabled)
        if enabled:
            self._on_pomodoro_config_changed()

    def _on_pomodoro_config_changed(self, *_args) -> None:
        self.view_model.update_pomodoro_config(
            focus_minutes=self._focus_spin.value(),
            break_minutes=self._break_spin.value(),
            total_cycles=self._cycles_spin.value(),
        )

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

        # Trava a configuração do Pomodoro enquanto uma sessão está rodando/pausada.
        self._pomodoro_checkbox.setEnabled(is_stopped)
        pomodoro_enabled = self.view_model.get_pomodoro_state().enabled
        for spin in (self._focus_spin, self._break_spin, self._cycles_spin):
            spin.setEnabled(is_stopped and pomodoro_enabled)

    def _on_pomodoro_state_changed(self, snapshot) -> None:
        self._phase_label.setText(snapshot.phase_label)

    def _read_minutes(self) -> int | None:
        raw_value = self._minutes_input.text().strip()
        try:
            minutes = int(raw_value)
        except ValueError:
            return None
        return minutes if minutes > 0 else None