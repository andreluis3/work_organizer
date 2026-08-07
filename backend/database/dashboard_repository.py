# backend/database/dashboard_repository.py
"""
Repositório de dados agregados para o Dashboard.

Responsabilidade única: executar consultas SQL e devolver dados brutos.
Nenhuma regra de negócio (XP, nível, streak, formatação) vive aqui —
isso é papel do DashboardService. Este arquivo é o único lugar do projeto
que sabe que "sessions" moram na tabela `pomodoro` e "goals" na `metas`.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta

from backend.database.conexao import conectar

WEEKDAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]


class DashboardRepository:
    def _connect(self) -> sqlite3.Connection:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Sessões (pomodoro)
    # ------------------------------------------------------------------

    def get_last_session(self) -> dict | None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, tarefa_id, inicio, fim, duracao_min, observacao
                FROM pomodoro
                ORDER BY datetime(inicio) DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)
        finally:
            conn.close()

    def get_today_sessions(self) -> tuple[int, int]:
        """Retorna (minutos_hoje, sessoes_hoje)."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            today = date.today().isoformat()
            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
                FROM pomodoro
                WHERE DATE(inicio) = DATE(?)
                """,
                (today,),
            )
            row = cursor.fetchone()
            if not row:
                return 0, 0
            return int(row["minutes"] or 0), int(row["sessions"] or 0)
        finally:
            conn.close()

    def get_week_sessions(self) -> list[dict]:
        """
        Retorna uma linha por dia dos últimos 7 dias:
        [{"label": "Seg", "minutes": 30, "sessions": 2}, ...]
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            today = date.today()
            week_rows: list[dict] = []
            for offset in range(6, -1, -1):
                current_day = today - timedelta(days=offset)
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
                    FROM pomodoro
                    WHERE DATE(inicio) = DATE(?)
                    """,
                    (current_day.isoformat(),),
                )
                row = cursor.fetchone()
                week_rows.append(
                    {
                        "label": WEEKDAY_LABELS[current_day.weekday()],
                        "minutes": int(row["minutes"] or 0) if row else 0,
                        "sessions": int(row["sessions"] or 0) if row else 0,
                    }
                )
            return week_rows
        finally:
            conn.close()

    def get_totals(self) -> tuple[int, int]:
        """Retorna (minutos_totais, sessoes_totais) desde sempre."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS minutes, COUNT(*) AS sessions
                FROM pomodoro
                """
            )
            row = cursor.fetchone()
            if not row:
                return 0, 0
            return int(row["minutes"] or 0), int(row["sessions"] or 0)
        finally:
            conn.close()

    def get_session_days(self) -> list[str]:
        """Datas (YYYY-MM-DD) distintas com pelo menos uma sessão. Usado pro streak."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT DATE(inicio) AS day
                FROM pomodoro
                ORDER BY day DESC
                """
            )
            return [row["day"] for row in cursor.fetchall() if row["day"]]
        finally:
            conn.close()

    def get_task_focus_totals(self, limit: int = 4) -> list[dict]:
        """[{"tarefa_id": 3, "minutes": 120}, ...] ordenado por minutos desc."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT tarefa_id, COALESCE(SUM(duracao_min), 0) AS minutes
                FROM pomodoro
                GROUP BY tarefa_id
                ORDER BY minutes DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def resolve_task_name(self, task_id: int | None) -> str | None:
        """
        Busca o título de uma task pelo id, tentando primeiro a tabela nova
        (`tasks`) e depois a legada (`tarefas`). Retorna None se não achar.
        """
        if not task_id:
            return None

        conn = self._connect()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT title FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row and row["title"]:
                return str(row["title"])

            cursor.execute("SELECT titulo FROM tarefas WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row and row["titulo"]:
                return str(row["titulo"])

            return None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Metas
    # ------------------------------------------------------------------

    def get_active_goal_target(self) -> int | None:
        """Horas-objetivo da meta ativa hoje, ou None se não houver meta cadastrada."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            today = date.today().isoformat()
            cursor.execute(
                """
                SELECT horas_objetivo
                FROM metas
                WHERE (
                    data_inicio IS NULL OR DATE(data_inicio) <= DATE(?)
                ) AND (
                    data_fim IS NULL OR DATE(data_fim) >= DATE(?)
                )
                ORDER BY id DESC
                LIMIT 1
                """,
                (today, today),
            )
            row = cursor.fetchone()
            if row and row["horas_objetivo"]:
                return int(row["horas_objetivo"])
            return None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Fallback de produtividade (usado apenas se TaskService não tiver dados)
    # ------------------------------------------------------------------

    def get_legacy_task_counts(self) -> tuple[int, int]:
        """(total, concluidas) na tabela legada `tarefas`."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM tarefas")
            total = int(cursor.fetchone()["total"] or 0)
            cursor.execute("SELECT COUNT(*) AS total FROM tarefas WHERE status = 'concluida'")
            completed = int(cursor.fetchone()["total"] or 0)
            return total, completed
        finally:
            conn.close()