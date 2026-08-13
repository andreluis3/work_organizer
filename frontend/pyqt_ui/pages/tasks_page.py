# frontend/pyqt_ui/pages/tasks_page.py
"""
Página de Tasks: hero de resumo, busca+filtros, 3 colunas Kanban
(Pendente/Pausada/Concluída), seção de Cursos e Histórico abaixo.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from frontend.pyqt_ui.dialogs.new_course_dialog import NewCourseDialog
from frontend.pyqt_ui.dialogs.new_task_dialog import NewTaskDialog
from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.viewmodels.tasks_viewmodel import (
    SORT_OPTIONS,
    CourseCardData,
    TaskChangeEvent,
    TasksViewModel,
)
from frontend.pyqt_ui.widgets.tasks.course_card import CourseCard
from frontend.pyqt_ui.widgets.tasks.history_section import HistorySection
from frontend.pyqt_ui.widgets.tasks.kanban_column import KanbanColumn
from frontend.pyqt_ui.widgets.tasks.task_card import TaskCard
from frontend.pyqt_ui.widgets.tasks.tasks_summary import TasksSummaryWidget


class TasksPage(BasePage):
    title = "Tasks"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tasksPage")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.title_label.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #172033;"
        )

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

        toolbar_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Buscar por titulo...")
        self.search_input.textChanged.connect(self._on_search_changed)
        toolbar_row.addWidget(self.search_input, stretch=1)

        sort_label = QLabel("Ordenar")
        sort_label.setObjectName("filterLabel")
        toolbar_row.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(list(SORT_OPTIONS.keys()))
        self.sort_combo.setCurrentText("Prioridade")
        self.sort_combo.currentTextChanged.connect(self.viewmodel.set_sort_option)
        toolbar_row.addWidget(self.sort_combo)

        new_task_btn = QPushButton("+ Nova Task")
        new_task_btn.setObjectName("primaryButton")
        new_task_btn.clicked.connect(self._open_new_task_dialog)
        toolbar_row.addWidget(new_task_btn)

        new_course_btn = QPushButton("+ Novo Curso")
        new_course_btn.clicked.connect(self._open_new_course_dialog)
        toolbar_row.addWidget(new_course_btn)

        toolbar_container = QWidget()
        toolbar_container.setObjectName("tasksToolbar")
        toolbar_container.setLayout(toolbar_row)
        self.add_content_widget(toolbar_container)

        # --- Kanban: 3 colunas lado a lado ---
        kanban_row = QHBoxLayout()
        kanban_row.setSpacing(14)

        self.pending_column = KanbanColumn("Pendente", "Nenhuma task pendente.")
        self.paused_column = KanbanColumn("Pausada", "Nenhuma task pausada.")
        self.done_column = KanbanColumn("Concluida", "Nenhuma task concluida ainda.")

        kanban_row.addWidget(self.pending_column, stretch=1)
        kanban_row.addWidget(self.paused_column, stretch=1)
        kanban_row.addWidget(self.done_column, stretch=1)

        kanban_container = QWidget()
        kanban_container.setObjectName("tasksKanban")
        kanban_container.setLayout(kanban_row)
        self.content_layout.addWidget(kanban_container, stretch=5)

        # --- Cursos + Histórico, lado a lado, abaixo do Kanban ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)

        self.courses_column = KanbanColumn("Cursos", "Nenhum curso cadastrado.")
        bottom_row.addWidget(self.courses_column, stretch=2)

        self.history_section = HistorySection()
        bottom_row.addWidget(self.history_section, stretch=1)

        bottom_container = QWidget()
        bottom_container.setObjectName("tasksBottom")
        bottom_container.setLayout(bottom_row)
        self.content_layout.addWidget(bottom_container, stretch=1)

        self._columns = {
            "pendente": self.pending_column,
            "pausada": self.paused_column,
            "concluida": self.done_column,
        }

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_show(self) -> None:
        super().on_show()
        self.viewmodel.refresh()

    # ------------------------------------------------------------------
    # Carga completa
    # ------------------------------------------------------------------

    def _on_loaded(self) -> None:
        self.summary_widget.update_data(self.viewmodel.summary)

        all_tasks = self.viewmodel.tasks_in_progress + self.viewmodel.tasks_done
        for status, column in self._columns.items():
            items = [
                (data.id, data.title, self._build_task_card(data))
                for data in all_tasks
                if data.status == status
            ]
            column.set_items(items)

        self.courses_column.set_items(
            [
                (data.id, data.title, self._build_course_card(data))
                for data in self.viewmodel.courses
            ]
        )
        self.history_section.set_items(self.viewmodel.history)

        if self.search_input.text():
            self._on_search_changed(self.search_input.text())

    # ------------------------------------------------------------------
    # Busca (client-side, sem nova consulta ao banco)
    # ------------------------------------------------------------------

    def _on_search_changed(self, text: str) -> None:
        for column in self._columns.values():
            column.filter_by_title(text)

    # ------------------------------------------------------------------
    # Atualizações granulares
    # ------------------------------------------------------------------

    def _on_task_changed(self, event: TaskChangeEvent) -> None:
        data = event.data
        target_column = self._columns.get(data.status)

        current_column = None
        for column in self._columns.values():
            if column.get(data.id) is not None:
                current_column = column
                break

        if current_column is target_column and current_column is not None:
            widget = current_column.get(data.id)
            widget.update_data(data)
            return

        if current_column is not None:
            current_column.remove(data.id)
        if target_column is not None:
            target_column.add(data.id, data.title, self._build_task_card(data))

        self.summary_widget.update_data(self.viewmodel.summary)

        if self.search_input.text():
            self._on_search_changed(self.search_input.text())

    def _on_course_changed(self, data: CourseCardData) -> None:
        widget = self.courses_column.get(data.id)
        if widget is not None:
            widget.update_data(data)

        if self.viewmodel.summary:
            self.summary_widget.update_data(self.viewmodel.summary)

    # ------------------------------------------------------------------
    # Construção de cards
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
            pass

    # ------------------------------------------------------------------
    # Diálogos
    # ------------------------------------------------------------------

    def _open_new_task_dialog(self) -> None:
        dialog = NewTaskDialog(parent=self)
        if dialog.exec():
            self.viewmodel.create_task(dialog.result_title, dialog.result_subtasks, dialog.result_priority)

    def _open_new_course_dialog(self) -> None:
        dialog = NewCourseDialog(parent=self)
        if dialog.exec():
            self.viewmodel.create_course(dialog.result_title, dialog.result_total_lessons)
