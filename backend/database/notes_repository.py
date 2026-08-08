"""
Repositório de Notes. SQL puro: CRUD, busca por título, pin.

A coluna `pinned` não existe no schema legado — este repositório garante
sua existência via ALTER TABLE idempotente na primeira instância, mesmo
padrão do _ensure_task_schema em tasks_db.py.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from backend.database.conexao import conectar

DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


class NotesRepository:
    def __init__(self) -> None:
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(notes)")
            columns = {row["name"] for row in cursor.fetchall()}
            if "pinned" not in columns:
                cursor.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER DEFAULT 0")
            conn.commit()
        finally:
            conn.close()

    def title_exists(self, title: str, ignore_id: int | None = None) -> bool:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            if ignore_id:
                cursor.execute("SELECT id FROM notes WHERE titulo = ? AND id != ?", (title, ignore_id))
            else:
                cursor.execute("SELECT id FROM notes WHERE titulo = ?", (title,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def insert_note(self, title: str, content: str) -> int:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            now = datetime.now().strftime(DATETIME_FMT)
            cursor.execute(
                """
                INSERT INTO notes (titulo, conteudo, data_criacao, data_atualizacao, pinned)
                VALUES (?, ?, ?, ?, 0)
                """,
                (title, content, now, now),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_note(self, note_id: int, title: str, content: str) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            now = datetime.now().strftime(DATETIME_FMT)
            cursor.execute(
                "UPDATE notes SET titulo = ?, conteudo = ?, data_atualizacao = ? WHERE id = ?",
                (title, content, now, note_id),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_note(self, note_id: int) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
        finally:
            conn.close()

    def set_pinned(self, note_id: int, pinned: bool) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET pinned = ? WHERE id = ?", (int(pinned), note_id))
            conn.commit()
        finally:
            conn.close()

    def list_notes(self) -> list[dict]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, titulo, data_atualizacao, pinned FROM notes ORDER BY pinned DESC, data_atualizacao DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_notes(self, term: str) -> list[dict]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, titulo, data_atualizacao, pinned FROM notes
                WHERE titulo LIKE ?
                ORDER BY pinned DESC, data_atualizacao DESC
                """,
                (f"%{term}%",),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_note(self, note_id: int) -> dict | None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo, conteudo, pinned FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()