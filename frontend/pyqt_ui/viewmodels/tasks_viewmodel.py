# frontend/pyqt_ui/viewmodels/tasks_viewmodel.py
"""
ViewModel da tela de Tasks.

Ponte entre TaskController (dados/ações crus) e os widgets Qt. Mantém um
cache em memória (id -> DTO) para permitir atualizações granulares: uma
ação de clique atualiza apenas o item afetado e ajusta os contadores do
resumo incrementalmente, sem recarregar a lista inteira do banco.

Recarga completa (`refresh()`) só acontece em: carga inicial, troca de
filtro/ordenação, criação de task/curso. Cliques em cards nunca disparam
uma recarga completa.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal

from backend.controllers.task_controller import TaskController

FILTER_OPTIONS = {
    "Todos": "todos",
    "Pendente": "pendente",
    "Pausada": "pausada",
    "Concluida": "concluida",
}
SORT_OPTIONS = {
    "Prioridade": "prioridade",
    "Mais recentes": "recentes",
}

PRIORITY_LABELS = {
    3: ("Alta", "#EF4444"),
    2: ("Media", "#EAB308"),
    1: ("Baixa", "#64748B"),
}
STATUS_LABELS = {
    "pendente": "Pendente",
    "pausada": "Pausada",
    "concluida": "Concluida",
}


# ----------------------------------------------------------------------
# DTOs de apresentação
# ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SubtaskViewData:
    id: int
    description: str
    completed: bool


@dataclass(frozen=True, slots=True)
class TaskCardData:
    id: int
    title: str
    status: str  # "pendente" | "pausada" | "concluida"
    status_label: str
    status_color: str
    is_done: bool
    priority_label: str
    priority_color: str
    created_at_label: str
    subtasks: list[SubtaskViewData] = field(default_factory=list)
    progress: float = 0.0


@dataclass(frozen=True, slots=True)
class CourseCardData:
    id: int
    title: str
    current_lesson: str
    total_lessons: int
    completed_lessons: int
    progress: float
    progress_label: str
    is_completed: bool = False


@dataclass(frozen=True, slots=True)
class HistoryItemData:
    title: str
    completed_at: str


@dataclass(frozen=True, slots=True)
class TasksSummaryData:
    total_label: str
    pending_label: str
    paused_label: str
    completed_label: str
    courses_in_progress_label: str


@dataclass(frozen=True, slots=True)
class TaskChangeEvent:
    """Payload do sinal `task_changed`: o card novo + se ele mudou de seção."""

    data: TaskCardData
    previous_is_done: bool

    @property
    def section_changed(self) -> bool:
        return self.previous_is_done != self.data.is_done


# ----------------------------------------------------------------------
# ViewModel
# ----------------------------------------------------------------------


class TasksViewModel(QObject):
    loaded = pyqtSignal()
    """Emitido em recarga completa (carga inicial, filtro/ordenação, criação)."""

    task_changed = pyqtSignal(object)  # TaskChangeEvent
    """Emitido quando UM task muda (toggle, ciclar status, subtask, título)."""

    course_changed = pyqtSignal(object)  # CourseCardData
    """Emitido quando UM curso tem o progresso atualizado."""

    def __init__(self, controller: TaskController | None = None) -> None:
        super().__init__()
        self.controller = controller or TaskController()

        self.status_filter_label = "Todos"
        self.sort_option_label = "Prioridade"

        self.tasks_in_progress: list[TaskCardData] = []
        self.tasks_done: list[TaskCardData] = []
        self.courses: list[CourseCardData] = []
        self.history: list[HistoryItemData] = []
        self.summary: TasksSummaryData | None = None

        self._tasks_by_id: dict[int, TaskCardData] = {}
        self._courses_by_id: dict[int, CourseCardData] = {}
        self._status_counts: dict[str, int] = {"pendente": 0, "pausada": 0, "concluida": 0}
        self._courses_in_progress_count = 0

    # ------------------------------------------------------------------
    # Recarga completa
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self.controller.clean_old_tasks()

        status = FILTER_OPTIONS.get(self.status_filter_label, "todos")
        sort_by = SORT_OPTIONS.get(self.sort_option_label, "prioridade")

        raw_items = self.controller.list_tasks(status_filter=status, sort_by=sort_by)
        raw_history = self.controller.get_history_items()

        raw_tasks = [item for item in raw_items if item.get("type") != "course"]
        raw_courses = [item for item in raw_items if item.get("type") == "course"]

        all_task_cards = [self._build_task(item) for item in raw_tasks]
        self.tasks_in_progress = [card for card in all_task_cards if not card.is_done]
        self.tasks_done = [card for card in all_task_cards if card.is_done]
        self.courses = [self._build_course(item) for item in raw_courses]
        self.history = [self._build_history(item) for item in raw_history]

        self._tasks_by_id = {card.id: card for card in all_task_cards}
        self._courses_by_id = {card.id: card for card in self.courses}

        self._status_counts = {"pendente": 0, "pausada": 0, "concluida": 0}
        for card in all_task_cards:
            self._status_counts[card.status] = self._status_counts.get(card.status, 0) + 1
        self._courses_in_progress_count = sum(1 for course in self.courses if not course.is_completed)

        self.summary = self._compose_summary()
        self.loaded.emit()

    def set_status_filter(self, label: str) -> None:
        self.status_filter_label = label
        self.refresh()

    def set_sort_option(self, label: str) -> None:
        self.sort_option_label = label
        self.refresh()

    # ------------------------------------------------------------------
    # Criação — únicas ações que ainda disparam recarga completa
    # ------------------------------------------------------------------

    def create_task(self, title: str, subtasks: list[str], priority: int) -> None:
        self.controller.create_task(title, subtasks, priority)
        self.refresh()

    def create_course(self, title: str, total_lessons: int) -> None:
        self.controller.create_course(title, total_lessons)
        self.refresh()

    # ------------------------------------------------------------------
    # Ações granulares — atualizam só o item afetado
    # ------------------------------------------------------------------

    def update_task_title(self, task_id: int, title: str) -> None:
        """Pode levantar ValueError (título vazio) — a View decide como exibir."""
        raw = self.controller.update_title(task_id, title)
        self._apply_task_update(raw)

    def toggle_task_completed(self, task_id: int, completed: bool) -> None:
        raw = self.controller.toggle_completed(task_id, completed)
        self._apply_task_update(raw)

    def cycle_task_status(self, task_id: int) -> None:
        raw = self.controller.cycle_status(task_id)
        self._apply_task_update(raw)

    def toggle_subtask_completed(self, subtask_id: int, completed: bool) -> None:
        raw = self.controller.set_subtask_completed(subtask_id, completed)
        self._apply_task_update(raw)

    def update_course_progress(
        self, task_id: int, completed_lessons: int, current_lesson: str, total_lessons: int
    ) -> None:
        self.controller.update_course_progress(task_id, completed_lessons, current_lesson, total_lessons)
        raw = self.controller.get_task(task_id)
        if not raw:
            return

        previous = self._courses_by_id.get(task_id)
        was_completed = previous.is_completed if previous else False

        data = self._build_course(raw)
        self._courses_by_id[task_id] = data

        if was_completed != data.is_completed:
            self._courses_in_progress_count += -1 if data.is_completed else 1
            self.summary = self._compose_summary()

        self.course_changed.emit(data)

    def _apply_task_update(self, raw: dict | None) -> None:
        if not raw:
            return

        previous = self._tasks_by_id.get(raw["id"])
        previous_status = previous.status if previous else None
        previous_is_done = previous.is_done if previous else False

        data = self._build_task(raw)
        self._tasks_by_id[data.id] = data

        if previous_status:
            self._status_counts[previous_status] = max(0, self._status_counts.get(previous_status, 0) - 1)
        self._status_counts[data.status] = self._status_counts.get(data.status, 0) + 1
        self.summary = self._compose_summary()

        event = TaskChangeEvent(data=data, previous_is_done=previous_is_done)
        self.task_changed.emit(event)

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------

    def _build_task(self, item: dict) -> TaskCardData:
        status = str(item.get("status") or "pendente")
        status_label = STATUS_LABELS.get(status, "Pendente")
        status_color = self._status_color(status)

        priority = int(item.get("prioridade", 1) or 1)
        priority_label, priority_color = PRIORITY_LABELS.get(priority, PRIORITY_LABELS[1])

        subtasks_raw = item.get("subtasks") or []
        subtasks = [
            SubtaskViewData(
                id=sub["id"],
                description=sub.get("description", ""),
                completed=bool(sub.get("completed")),
            )
            for sub in subtasks_raw
        ]

        if subtasks:
            completed_count = sum(1 for sub in subtasks if sub.completed)
            progress = completed_count / len(subtasks)
        else:
            progress = 1.0 if status == "concluida" else 0.0

        return TaskCardData(
            id=item["id"],
            title=item.get("title", "Task"),
            status=status,
            status_label=status_label,
            status_color=status_color,
            is_done=status == "concluida",
            priority_label=priority_label,
            priority_color=priority_color,
            created_at_label=self._format_date(item.get("created_at")),
            subtasks=subtasks,
            progress=progress,
        )

    def _build_course(self, item: dict) -> CourseCardData:
        course = item.get("course") or {}
        total = max(1, int(course.get("total_lessons", 1) or 1))
        progress_percent = int(course.get("progress", 0) or 0)
        completed_lessons = int(round((progress_percent / 100) * total))

        return CourseCardData(
            id=item["id"],
            title=item.get("title", "Curso"),
            current_lesson=course.get("current_lesson") or "Aula 1",
            total_lessons=total,
            completed_lessons=completed_lessons,
            progress=progress_percent / 100,
            progress_label=f"{completed_lessons}/{total} aulas",
            is_completed=progress_percent >= 100,
        )

    def _build_history(self, item: dict) -> HistoryItemData:
        return HistoryItemData(
            title=item.get("title", ""),
            completed_at=self._format_date(item.get("completed_at")),
        )

    def _compose_summary(self) -> TasksSummaryData:
        total = sum(self._status_counts.values())
        return TasksSummaryData(
            total_label=str(total),
            pending_label=str(self._status_counts.get("pendente", 0)),
            paused_label=str(self._status_counts.get("pausada", 0)),
            completed_label=str(self._status_counts.get("concluida", 0)),
            courses_in_progress_label=str(self._courses_in_progress_count),
        )

    # ------------------------------------------------------------------
    # Formatadores privados
    # ------------------------------------------------------------------

    def _status_color(self, status: str) -> str:
        if status == "concluida":
            return "#16A34A"
        if status == "pausada":
            return "#CA8A04"
        return "#2563EB"

    def _format_date(self, value: str | None) -> str:
        if not value:
            return "--"
        return str(value)[:16].replace("T", " ")