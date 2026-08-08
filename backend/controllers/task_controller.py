from datetime import datetime, timedelta

from backend.services.task_service import TaskService

DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

class TaskController:
    def __init__(self, service=None):
        self.service = service or TaskService()

    def create_task(self, title, subtasks=None, prioridade=1):
        return self.service.create_task(title, subtasks, prioridade)

    def create_course(self, title, total_lessons):
        return self.service.create_course(title, total_lessons)

    def list_tasks(self, status_filter="todos", sort_by="recentes"):
        return self.service.list_tasks(status_filter, sort_by)

    def update_title(self, task_id, title):
        return self.service.update_title(task_id, title)

    def toggle_completed(self, task_id, completed):
        return self.service.set_completed(task_id, completed)

    def cycle_status(self, task_id):
        return self.service.toggle_status(task_id)

    def set_subtask_completed(self, subtask_id, completed):
        return self.service.set_subtask_completed(subtask_id, completed)

    def update_course_progress(self, task_id, completed_lessons, current_lesson, total_lessons):
        return self.service.update_course_progress(
            task_id,
            completed_lessons,
            current_lesson,
            total_lessons,
        )

    def get_history_items(self):
        return self.service.get_history_items()
    
    def clean_old_tasks(self, hours: int = 48) -> int:
        """Move tasks concluídas há mais de `hours` horas para o histórico."""
        cutoff = (datetime.now() - timedelta(hours=hours)).strftime(DATETIME_FMT)
        return self.service.move_completed_to_history(cutoff)

    def get_stagnant_tasks(self, days: int = 7) -> list[dict]:
        """Tasks não concluídas sem atualização há mais de `days` dias."""
        cutoff = (datetime.now() - timedelta(days=days)).strftime(DATETIME_FMT)
        return self.service.get_stagnant_tasks(cutoff)

    def get_task(self, task_id: int) -> dict | None:
        return self.service.get_task(task_id)
    
    