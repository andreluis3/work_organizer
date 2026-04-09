import sqlite3
from datetime import datetime

from backend.database.conexao import conectar


DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


def _now_str():
    return datetime.now().strftime(DATETIME_FMT)


def _dict_rows(cursor):
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def _get_conn():
    conn = conectar()
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            type TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            description TEXT,
            completed INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            current_lesson TEXT,
            total_lessons INTEGER,
            progress INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            title TEXT,
            completed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_task(title, type):
    conn = _get_conn()
    cursor = conn.cursor()
    now = _now_str()

    cursor.execute("""
        INSERT INTO tasks (title, type, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (title, type, "pending", now, now))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def add_subtask(task_id, description):
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO subtasks (task_id, description, completed)
        VALUES (?, ?, ?)
    """, (task_id, description, 0))

    subtask_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return subtask_id


def get_tasks():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tasks
        ORDER BY created_at DESC
    """)
    tasks = _dict_rows(cursor)
    conn.close()
    return tasks


def get_task(task_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tasks WHERE id = ?
    """, (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_subtasks(task_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM subtasks
        WHERE task_id = ?
        ORDER BY id ASC
    """, (task_id,))
    subtasks = _dict_rows(cursor)
    conn.close()
    return subtasks


def get_subtask(subtask_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM subtasks WHERE id = ?
    """, (subtask_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_subtask_status(subtask_id, completed):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE subtasks
        SET completed = ?
        WHERE id = ?
    """, (int(completed), subtask_id))
    conn.commit()
    conn.close()


def update_task_status(task_id, status):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (status, _now_str(), task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM courses WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()


def create_course(task_id, total_lessons, current_lesson="Aula 1", progress=0):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO courses (task_id, current_lesson, total_lessons, progress)
        VALUES (?, ?, ?, ?)
    """, (task_id, current_lesson, int(total_lessons), int(progress)))
    course_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return course_id


def get_course(task_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM courses WHERE task_id = ?
    """, (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_course(task_id, current_lesson, total_lessons, progress):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE courses
        SET current_lesson = ?, total_lessons = ?, progress = ?
        WHERE task_id = ?
    """, (current_lesson, int(total_lessons), int(progress), task_id))
    conn.commit()
    conn.close()


def add_history(task_id, title, completed_at):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (task_id, title, completed_at)
        VALUES (?, ?, ?)
    """, (task_id, title, completed_at))
    conn.commit()
    conn.close()


def get_history():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM history
        ORDER BY completed_at DESC
    """)
    history = _dict_rows(cursor)
    conn.close()
    return history
