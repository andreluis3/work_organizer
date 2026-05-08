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


def _column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row["name"] == column for row in cursor.fetchall())


def _ensure_task_schema(cursor):
    additions = {
        "type": "TEXT DEFAULT 'task'",
        "status": "TEXT DEFAULT 'pendente'",
        "prioridade": "INTEGER DEFAULT 1",
        "concluida": "INTEGER DEFAULT 0",
        "created_at": "TEXT",
        "updated_at": "TEXT",
    }

    for column, definition in additions.items():
        if not _column_exists(cursor, "tasks", column):
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {column} {definition}")

    now = _now_str()
    cursor.execute("UPDATE tasks SET type = COALESCE(type, 'task')")
    cursor.execute("UPDATE tasks SET prioridade = COALESCE(prioridade, 1)")
    cursor.execute("UPDATE tasks SET created_at = COALESCE(created_at, ?)", (now,))
    cursor.execute("UPDATE tasks SET updated_at = COALESCE(updated_at, created_at, ?)", (now,))
    cursor.execute("""
        UPDATE tasks
        SET status = CASE
            WHEN status IN ('done', 'concluida') THEN 'concluida'
            WHEN status IN ('paused', 'pausada') THEN 'pausada'
            WHEN status IN ('in_progress', 'pending', 'pendente') THEN 'pendente'
            ELSE 'pendente'
        END
    """)
    cursor.execute("""
        UPDATE tasks
        SET concluida = CASE WHEN status = 'concluida' THEN 1 ELSE COALESCE(concluida, 0) END
    """)


def create_tables():
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            type TEXT,
            status TEXT,
            prioridade INTEGER DEFAULT 1,
            concluida INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    _ensure_task_schema(cursor)

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


def create_task(title, type="task", prioridade=1):
    conn = _get_conn()
    cursor = conn.cursor()
    now = _now_str()

    cursor.execute("""
        INSERT INTO tasks (title, type, status, prioridade, concluida, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, type, "pendente", int(prioridade), 0, now, now))

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


def get_tasks(status=None, order_by="recentes"):
    conn = _get_conn()
    cursor = conn.cursor()

    params = []
    where = ""
    if status and status != "todos":
        where = "WHERE status = ?"
        params.append(status)

    order_clause = "ORDER BY created_at DESC, id DESC"
    if order_by == "prioridade":
        order_clause = "ORDER BY prioridade DESC, created_at DESC, id DESC"

    cursor.execute(f"""
        SELECT * FROM tasks
        {where}
        {order_clause}
    """, params)
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
    concluida = 1 if status == "concluida" else 0
    cursor.execute("""
        UPDATE tasks
        SET status = ?, concluida = ?, updated_at = ?
        WHERE id = ?
    """, (status, concluida, _now_str(), task_id))
    conn.commit()
    conn.close()


def update_task_title(task_id, title):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?, updated_at = ?
        WHERE id = ?
    """, (title, _now_str(), task_id))
    conn.commit()
    conn.close()


def update_task_completion(task_id, concluida):
    status = "concluida" if int(concluida) else "pendente"
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET concluida = ?, status = ?, updated_at = ?
        WHERE id = ?
    """, (int(concluida), status, _now_str(), task_id))
    conn.commit()
    conn.close()


def update_task_priority(task_id, prioridade):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET prioridade = ?, updated_at = ?
        WHERE id = ?
    """, (int(prioridade), _now_str(), task_id))
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
