from datetime import datetime, timedelta

from backend.database import tasks_db
from backend.services.task_service import TaskService


DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
STAGNANT_DAYS = 7
_service = TaskService()


def _ensure_tables():
    tasks_db.create_tables()


def _parse_dt(value):
    try:
        return datetime.strptime(value, DATETIME_FMT)
    except (TypeError, ValueError):
        return None


def create_task(title, subtasks):
    return _service.create_task(title, subtasks)


def create_course(title, total_lessons):
    return _service.create_course(title, total_lessons)


def get_all_tasks():
    return _service.list_tasks()


def get_task_with_subtasks(task_id):
    return _service.get_task(task_id)


def complete_subtask(subtask_id):
    task = _service.set_subtask_completed(subtask_id, True)
    return task["id"] if task else None


def set_subtask_status(subtask_id, completed):
    task = _service.set_subtask_completed(subtask_id, completed)
    return task["id"] if task else None


def complete_task_if_finished(task_id):
    task = _service.get_task(task_id)
    if not task or not task.get("subtasks"):
        return False
    all_done = all(subtask.get("completed") for subtask in task["subtasks"])
    _service.update_status(task_id, "concluida" if all_done else "pendente")
    return all_done


def update_course_progress(task_id, completed_lessons, current_lesson, total_lessons):
    return _service.update_course_progress(task_id, completed_lessons, current_lesson, total_lessons)


def get_stagnant_tasks():
    _ensure_tables()
    tasks = get_all_tasks()
    cutoff = datetime.now() - timedelta(days=STAGNANT_DAYS)
    stagnant = []

    for task in tasks:
        if task.get("status") == "concluida":
            continue
        updated = _parse_dt(task.get("updated_at"))
        if updated and updated < cutoff:
            stagnant.append(task)

    return stagnant


def clean_old_tasks():
    _ensure_tables()
    tasks = tasks_db.get_tasks()
    cutoff = datetime.now() - timedelta(hours=48)
    moved = 0

    for task in tasks:
        if task.get("status") != "concluida":
            continue
        updated = _parse_dt(task.get("updated_at"))
        if updated and updated <= cutoff:
            tasks_db.add_history(task["id"], task["title"], task.get("updated_at"))
            tasks_db.delete_task(task["id"])
            moved += 1

    return moved


def get_history_items():
    return _service.get_history_items()
