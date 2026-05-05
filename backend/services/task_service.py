from backend.database import tasks_db


VALID_STATUSES = ("pendente", "pausada", "concluida")
VALID_FILTERS = ("todos", *VALID_STATUSES)
VALID_SORTS = ("prioridade", "recentes")
STATUS_FLOW = {
    "pendente": "pausada",
    "pausada": "concluida",
    "concluida": "pendente",
}
LEGACY_STATUS_MAP = {
    "pending": "pendente",
    "in_progress": "pendente",
    "done": "concluida",
    "paused": "pausada",
}


class TaskService:
    def __init__(self, repository=tasks_db):
        self.repository = repository
        self.repository.create_tables()

    def create_task(self, title, subtasks=None, prioridade=1):
        clean_title = self._clean_title(title)
        priority = self._normalize_priority(prioridade)
        task_id = self.repository.create_task(clean_title, "task", priority)

        for description in subtasks or []:
            desc = str(description).strip()
            if desc:
                self.repository.add_subtask(task_id, desc)

        return task_id

    def create_course(self, title, total_lessons):
        clean_title = self._clean_title(title)
        total = max(1, int(total_lessons))
        task_id = self.repository.create_task(clean_title, "course", 1)
        self.repository.create_course(
            task_id,
            total_lessons=total,
            current_lesson="Aula 1",
            progress=0,
        )
        return task_id

    def list_tasks(self, status_filter="todos", sort_by="recentes"):
        status = self._normalize_filter(status_filter)
        order = sort_by if sort_by in VALID_SORTS else "recentes"
        tasks = self.repository.get_tasks(status=status, order_by=order)
        return [self._enrich_task(task) for task in tasks]

    def get_task(self, task_id):
        task = self.repository.get_task(task_id)
        return self._enrich_task(task) if task else None

    def update_title(self, task_id, title):
        clean_title = self._clean_title(title)
        self.repository.update_task_title(task_id, clean_title)
        return self.get_task(task_id)

    def update_status(self, task_id, status):
        next_status = self._normalize_status(status)
        self.repository.update_task_status(task_id, next_status)
        return self.get_task(task_id)

    def toggle_status(self, task_id):
        task = self.repository.get_task(task_id)
        if not task:
            return None
        current = self._normalize_status(task.get("status"))
        return self.update_status(task_id, STATUS_FLOW[current])

    def set_completed(self, task_id, completed):
        self.repository.update_task_completion(task_id, 1 if completed else 0)
        return self.get_task(task_id)

    def set_subtask_completed(self, subtask_id, completed):
        subtask = self.repository.get_subtask(subtask_id)
        if not subtask:
            return None

        self.repository.update_subtask_status(subtask_id, int(bool(completed)))
        self._sync_task_from_subtasks(subtask["task_id"])
        return self.get_task(subtask["task_id"])

    def update_course_progress(self, task_id, completed_lessons, current_lesson, total_lessons):
        total = max(1, int(total_lessons))
        completed = max(0, min(int(completed_lessons), total))
        progress = int((completed / total) * 100)
        self.repository.update_course(task_id, current_lesson, total, progress)
        self.repository.update_task_status(
            task_id,
            "concluida" if progress >= 100 else "pendente",
        )
        return progress

    def get_stagnant_tasks(self, cutoff):
        tasks = self.list_tasks()
        stagnant = []
        for task in tasks:
            if task.get("status") == "concluida":
                continue
            updated_at = task.get("updated_at")
            if updated_at and updated_at < cutoff:
                stagnant.append(task)
        return stagnant

    def move_completed_to_history(self, cutoff):
        moved = 0
        for task in self.repository.get_tasks():
            if self._normalize_status(task.get("status")) != "concluida":
                continue
            updated_at = task.get("updated_at")
            if updated_at and updated_at <= cutoff:
                self.repository.add_history(task["id"], task["title"], updated_at)
                self.repository.delete_task(task["id"])
                moved += 1
        return moved

    def get_history_items(self):
        return self.repository.get_history()

    def _sync_task_from_subtasks(self, task_id):
        subtasks = self.repository.get_subtasks(task_id)
        if not subtasks:
            return False

        all_done = all(subtask.get("completed") for subtask in subtasks)
        self.repository.update_task_status(
            task_id,
            "concluida" if all_done else "pendente",
        )
        return all_done

    def _enrich_task(self, task):
        data = dict(task)
        data["status"] = self._normalize_status(data.get("status"))
        data["concluida"] = 1 if data["status"] == "concluida" else int(data.get("concluida") or 0)
        data["prioridade"] = self._normalize_priority(data.get("prioridade", 1))

        if data.get("type") == "task":
            data["subtasks"] = self.repository.get_subtasks(data["id"])
            data["course"] = None
        elif data.get("type") == "course":
            data["subtasks"] = []
            data["course"] = self.repository.get_course(data["id"])
        else:
            data["subtasks"] = []
            data["course"] = None
        return data

    def _normalize_status(self, status):
        value = str(status or "pendente").strip().lower()
        value = LEGACY_STATUS_MAP.get(value, value)
        if value not in VALID_STATUSES:
            return "pendente"
        return value

    def _normalize_filter(self, status_filter):
        value = str(status_filter or "todos").strip().lower()
        value = LEGACY_STATUS_MAP.get(value, value)
        return value if value in VALID_FILTERS else "todos"

    def _normalize_priority(self, prioridade):
        try:
            value = int(prioridade)
        except (TypeError, ValueError):
            value = 1
        return max(1, min(value, 3))

    def _clean_title(self, title):
        clean = str(title or "").strip()
        if not clean:
            raise ValueError("O titulo da task nao pode ficar vazio.")
        return clean
