from datetime import datetime, timedelta

from backend.database import tasks_db


DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
STAGNANT_DAYS = 7


def _ensure_tables():
    tasks_db.create_tables()


def _parse_dt(value):
    try:
        return datetime.strptime(value, DATETIME_FMT)
    except (TypeError, ValueError):
        return None


def create_task(title, subtasks):
    _ensure_tables()
    task_id = tasks_db.create_task(title, "task")

    for description in subtasks:
        desc = description.strip()
        if desc:
            tasks_db.add_subtask(task_id, desc)

    return task_id


def create_course(title, total_lessons):
    _ensure_tables()
    task_id = tasks_db.create_task(title, "course")
    total = max(1, int(total_lessons))
    tasks_db.create_course(task_id, total_lessons=total, current_lesson="Aula 1", progress=0)
    return task_id


def get_all_tasks():
    _ensure_tables()
    tasks = tasks_db.get_tasks()
    enriched = []

    for task in tasks:
        data = dict(task)
        if task.get("type") == "task":
            data["subtasks"] = tasks_db.get_subtasks(task["id"])
            data["course"] = None
        elif task.get("type") == "course":
            data["subtasks"] = []
            data["course"] = tasks_db.get_course(task["id"])
        else:
            data["subtasks"] = []
            data["course"] = None
        enriched.append(data)

    return enriched


def get_task_with_subtasks(task_id):
    _ensure_tables()
    task = tasks_db.get_task(task_id)
    if not task:
        return None
    task["subtasks"] = tasks_db.get_subtasks(task_id)
    task["course"] = tasks_db.get_course(task_id) if task.get("type") == "course" else None
    return task


def complete_subtask(subtask_id):
    _ensure_tables()
    subtask = tasks_db.get_subtask(subtask_id)
    if not subtask:
        return None

    tasks_db.update_subtask_status(subtask_id, 1)
    complete_task_if_finished(subtask["task_id"])
    return subtask["task_id"]


def set_subtask_status(subtask_id, completed):
    _ensure_tables()
    subtask = tasks_db.get_subtask(subtask_id)
    if not subtask:
        return None

    tasks_db.update_subtask_status(subtask_id, int(bool(completed)))
    if completed:
        complete_task_if_finished(subtask["task_id"])
    else:
        tasks_db.update_task_status(subtask["task_id"], "in_progress")
    return subtask["task_id"]


def complete_task_if_finished(task_id):
    _ensure_tables()
    subtasks = tasks_db.get_subtasks(task_id)
    if not subtasks:
        return False

    all_done = all(subtask.get("completed") for subtask in subtasks)
    if all_done:
        tasks_db.update_task_status(task_id, "done")
    else:
        tasks_db.update_task_status(task_id, "in_progress")
    return all_done


def update_course_progress(task_id, completed_lessons, current_lesson, total_lessons):
    _ensure_tables()
    total = max(1, int(total_lessons))
    completed = max(0, min(int(completed_lessons), total))
    progress = int((completed / total) * 100)
    tasks_db.update_course(task_id, current_lesson, total, progress)
    if progress >= 100:
        tasks_db.update_task_status(task_id, "done")
    else:
        tasks_db.update_task_status(task_id, "in_progress")
    return progress


def get_stagnant_tasks():
    _ensure_tables()
    tasks = get_all_tasks()
    cutoff = datetime.now() - timedelta(days=STAGNANT_DAYS)
    stagnant = []

    for task in tasks:
        if task.get("status") == "done":
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
        if task.get("status") != "done":
            continue
        updated = _parse_dt(task.get("updated_at"))
        if updated and updated <= cutoff:
            tasks_db.add_history(task["id"], task["title"], task.get("updated_at"))
            tasks_db.delete_task(task["id"])
            moved += 1

    return moved


def get_history_items():
    _ensure_tables()
    return tasks_db.get_history()
