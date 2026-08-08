# frontend/pyqt_ui/pages/tasks_page.py
"""
Página de Tasks: header com ações, filtros, hero de resumo, seções de
tasks (em andamento/concluídas), cursos e histórico.

Orquestra o TasksViewModel e os widgets — nenhuma regra de negócio aqui.
Atualizações de clique (toggle, status, subtask, progresso de curso) só
tocam o widget afetado, nunca reconstroem a tela inteira.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from frontend.pyqt_ui.dialogs.new_course_dialog import NewCourseDialog
from frontend.pyqt_ui.dialogs.new_task_dialog import NewTaskDialog
from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.viewmodels.tasks_viewmodel import (
    FILTER_OPTIONS,
    SORT_OPTIONS,
    CourseCardData,
    TaskChangeEvent,
    TasksViewModel,
)
from frontend.pyqt_ui.widgets.tasks.course_card import CourseCard
from frontend.pyqt_ui.widgets.tasks.history_section import HistorySection
from frontend.pyqt_ui.widgets.tasks.task_card import TaskCard
from frontend.pyqt_ui.widgets.tasks.task_section import TaskSection
from frontend.pyqt_ui.widgets.tasks.tasks_summary import TasksSummaryWidget


class TasksPage(BasePage):
    title = "Tasks"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.viewmodel = TasksViewModel()
        self.viewmodel.loaded.connect(self._on_loaded)
        self.viewmodel.task_changed.connect(self._on_task_changed)
        self.viewmodel.course_changed.connect(self._on_course_changed)

        self._build_ui()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.summary_widget = TasksSummaryWidget()
        self.add_content_widget(self.summary_widget)

        actions_row = QHBoxLayout()

        filter_label = QLabel("Status")
        filter_label.setObjectName("filterLabel")
        actions_row.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(list(FILTER_OPTIONS.keys()))
        self.filter_combo.setCurrentText("Todos")
        self.filter_combo.currentTextChanged.connect(self.viewmodel.set_status_filter)
        actions_row.addWidget(self.filter_combo)

        sort_label = QLabel("Ordenar")
        sort_label.setObjectName("filterLabel")
        actions_row.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(list(SORT_OPTIONS.keys()))
        self.sort_combo.setCurrentText("Prioridade")
        self.sort_combo.currentTextChanged.connect(self.viewmodel.set_sort_option)
        actions_row.addWidget(self.sort_combo)

        actions_row.addStretch(1)

        new_task_btn = QPushButton("+ Nova Task")
        new_task_btn.setObjectName("primaryButton")
        new_task_btn.clicked.connect(self._open_new_task_dialog)
        actions_row.addWidget(new_task_btn)

        new_course_btn = QPushButton("+ Novo Curso")
        new_course_btn.clicked.connect(self._open_new_course_dialog)
        actions_row.addWidget(new_course_btn)

        actions_container = QWidget()
        actions_container.setLayout(actions_row)
        self.add_content_widget(actions_container)

        splitter = QSplitter()

        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        self.in_progress_section = TaskSection("Em andamento", "Nenhuma task em andamento.")
        left_layout.addWidget(self.in_progress_section, stretch=1)

        self.done_section = TaskSection("Concluidas", "Nenhuma task concluida ainda.")
        left_layout.addWidget(self.done_section, stretch=1)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        self.courses_section = TaskSection("Cursos", "Nenhum curso cadastrado.")
        right_layout.addWidget(self.courses_section, stretch=1)

        self.history_section = HistorySection()
        right_layout.addWidget(self.history_section, stretch=1)

        splitter.addWidget(left_column)
        splitter.addWidget(right_column)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        self.add_content_widget(splitter)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_show(self) -> None:
        super().on_show()
        self.viewmodel.refresh()

    # ------------------------------------------------------------------
    # Carga completa (filtro/ordenação/carga inicial)
    # ------------------------------------------------------------------

    def _on_loaded(self) -> None:
        self.summary_widget.update_data(self.viewmodel.summary)

        self.in_progress_section.set_items(
            [(data.id, self._build_task_card(data)) for data in self.viewmodel.tasks_in_progress]
        )
        self.done_section.set_items(
            [(data.id, self._build_task_card(data)) for data in self.viewmodel.tasks_done]
        )
        self.courses_section.set_items(
            [(data.id, self._build_course_card(data)) for data in self.viewmodel.courses]
        )
        self.history_section.set_items(self.viewmodel.history)

    # ------------------------------------------------------------------
    # Atualizações granulares
    # ------------------------------------------------------------------

    def _on_task_changed(self, event: TaskChangeEvent) -> None:
        data = event.data

        if not event.section_changed:
            widget = self.in_progress_section.get(data.id) or self.done_section.get(data.id)
            if widget is not None:
                widget.update_data(data)
            return

        # mudou de seção: remove de onde estava, adiciona na nova
        self.in_progress_section.remove(data.id)
        self.done_section.remove(data.id)

        target_section = self.done_section if data.is_done else self.in_progress_section
        target_section.add(data.id, self._build_task_card(data))

        self.summary_widget.update_data(self.viewmodel.summary)

    def _on_course_changed(self, data: CourseCardData) -> None:
        widget = self.courses_section.get(data.id)
        if widget is not None:
            widget.update_data(data)

        if self.viewmodel.summary:
            self.summary_widget.update_data(self.viewmodel.summary)

    # ------------------------------------------------------------------
    # Construção de cards (conecta sinais uma única vez, na criação)
    # ------------------------------------------------------------------

    def _build_task_card(self, data) -> TaskCard:
        card = TaskCard(data)
        card.title_edited.connect(self._safe_update_title)
        card.completed_toggled.connect(self.viewmodel.toggle_task_completed)
        card.status_cycled.connect(self.viewmodel.cycle_task_status)
        card.subtask_toggled.connect(self.viewmodel.toggle_subtask_completed)
        return card

    def _build_course_card(self, data: CourseCardData) -> CourseCard:
        card = CourseCard(data)
        card.progress_updated.connect(self.viewmodel.update_course_progress)
        return card

    def _safe_update_title(self, task_id: int, title: str) -> None:
        try:
            self.viewmodel.update_task_title(task_id, title)
        except ValueError:
            pass  # título vazio já é bloqueado no próprio TaskCard antes de emitir

    # ------------------------------------------------------------------
    # Diálogos
    # ------------------------------------------------------------------

    def _open_new_task_dialog(self) -> None:
        dialog = NewTaskDialog(parent=self)
        if dialog.exec():
            self.viewmodel.create_task(
                dialog.result_title,
                dialog.result_subtasks,
                dialog.result_priority,
            )

    def _open_new_course_dialog(self) -> None:
        dialog = NewCourseDialog(parent=self)
        if dialog.exec():
            self.viewmodel.create_course(dialog.result_title, dialog.result_total_lessons)