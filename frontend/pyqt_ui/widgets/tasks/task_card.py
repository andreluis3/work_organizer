# frontend/pyqt_ui/widgets/tasks/task_card.py
"""
Card de uma task (não-curso): título editável, checkbox de conclusão,
badge de prioridade, botão de status cíclico, subtasks e progress bar.

Widget "burro" com interação: nunca chama TaskController nem ViewModel
diretamente — apenas emite sinais. Quem decide o que fazer com a ação
(persistir, recarregar) é a TasksPage.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from frontend.pyqt_ui.viewmodels.tasks_viewmodel import TaskCardData


class TaskCard(QFrame):
    title_edited = pyqtSignal(int, str)  # task_id, new_title
    completed_toggled = pyqtSignal(int, bool)  # task_id, completed
    status_cycled = pyqtSignal(int)  # task_id
    subtask_toggled = pyqtSignal(int, bool)  # subtask_id, completed

    TITLE_PAGE = 0
    EDIT_PAGE = 1

    def __init__(self, data: TaskCardData, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("taskCard")
        self.data = data
        self._subtask_checkboxes: dict[int, QCheckBox] = {}

        self._build_ui()
        self.update_data(data)

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.completed_checkbox = QCheckBox()
        self.completed_checkbox.setObjectName("taskCompletedCheckbox")
        self.completed_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.completed_checkbox.toggled.connect(self._on_completed_toggled)
        top_row.addWidget(self.completed_checkbox)

        self.title_stack = QStackedWidget()

        self.title_label = QLabel()
        self.title_label.setObjectName("taskTitle")
        self.title_label.setCursor(Qt.CursorShape.IBeamCursor)
        self.title_label.mousePressEvent = self._start_inline_edit  # type: ignore[method-assign]
        self.title_stack.addWidget(self.title_label)

        self.title_input = QLineEdit()
        self.title_input.setObjectName("taskTitleInput")
        self.title_input.returnPressed.connect(self._save_inline_edit)
        self.title_input.editingFinished.connect(self._save_inline_edit)
        self.title_stack.addWidget(self.title_input)

        self.title_stack.setCurrentIndex(self.TITLE_PAGE)
        top_row.addWidget(self.title_stack, stretch=1)

        self.priority_badge = QLabel()
        self.priority_badge.setObjectName("priorityBadge")
        self.priority_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.priority_badge.setFixedWidth(64)
        top_row.addWidget(self.priority_badge)

        self.status_button = QPushButton()
        self.status_button.setObjectName("statusButton")
        self.status_button.setFixedWidth(100)
        self.status_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_button.clicked.connect(lambda: self.status_cycled.emit(self.data.id))
        top_row.addWidget(self.status_button)

        root.addLayout(top_row)

        self.subtasks_container = QWidget()
        self.subtasks_layout = QVBoxLayout(self.subtasks_container)
        self.subtasks_layout.setContentsMargins(34, 0, 0, 0)
        self.subtasks_layout.setSpacing(4)
        root.addWidget(self.subtasks_container)

        self.created_at_label = QLabel()
        self.created_at_label.setObjectName("taskCreatedAt")
        root.addWidget(self.created_at_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("taskProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)

    # ------------------------------------------------------------------
    # Atualização de dados
    # ------------------------------------------------------------------

    def update_data(self, data: TaskCardData) -> None:
        self.data = data

        self.completed_checkbox.blockSignals(True)
        self.completed_checkbox.setChecked(data.is_done)
        self.completed_checkbox.blockSignals(False)

        self.title_label.setText(data.title)
        self.title_label.setProperty("done", "true" if data.is_done else "false")
        self._refresh_style(self.title_label)

        self.priority_badge.setText(data.priority_label)
        self.priority_badge.setStyleSheet(
            f"background-color: {data.priority_color}; color: #0B1120; border-radius: 6px; font-weight: 700;"
        )

        self.status_button.setText(data.status_label)
        self.status_button.setStyleSheet(
            f"background-color: {data.status_color}; color: #FFFFFF; border-radius: 6px; font-weight: 600;"
        )

        priority_key = {"Alta": "alta", "Media": "media", "Baixa": "baixa"}.get(data.priority_label, "baixa")
        self.setProperty("priority", priority_key)
        self._refresh_style(self)

        self.priority_badge.setText(data.priority_label)
        self.priority_badge.setStyleSheet(
            f"background-color: {data.priority_color}; color: #0B1120; font-weight: 700;"
        )

        self.created_at_label.setText(f"Criada em {data.created_at_label}")

        self._render_subtasks(data.subtasks)
        self.progress_bar.setValue(int(data.progress * 100))

    def _render_subtasks(self, subtasks) -> None:
        while self.subtasks_layout.count():
            item = self.subtasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._subtask_checkboxes.clear()

        for subtask in subtasks:
            checkbox = QCheckBox(subtask.description)
            checkbox.setObjectName("subtaskCheckbox")
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
            checkbox.setChecked(subtask.completed)
            checkbox.toggled.connect(
                lambda checked, subtask_id=subtask.id: self.subtask_toggled.emit(subtask_id, checked)
            )
            self.subtasks_layout.addWidget(checkbox)
            self._subtask_checkboxes[subtask.id] = checkbox

    # ------------------------------------------------------------------
    # Edição inline do título
    # ------------------------------------------------------------------

    def _start_inline_edit(self, _event=None) -> None:
        self.title_input.setText(self.data.title)
        self.title_stack.setCurrentIndex(self.EDIT_PAGE)
        self.title_input.setFocus()
        self.title_input.selectAll()

    def _save_inline_edit(self) -> None:
        if self.title_stack.currentIndex() != self.EDIT_PAGE:
            return

        new_title = self.title_input.text().strip()
        self.title_stack.setCurrentIndex(self.TITLE_PAGE)

        if not new_title or new_title == self.data.title:
            return

        self.title_edited.emit(self.data.id, new_title)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_completed_toggled(self, checked: bool) -> None:
        self.completed_toggled.emit(self.data.id, checked)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)