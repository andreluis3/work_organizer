from __future__ import annotations

from datetime import date, datetime

from backend.database.conexao import conectar


class PomodoroRepository:
    """Acesso a dados da tabela `pomodoro`. Só SQL, nenhuma regra de negócio."""

    def registrar_sessao(
        self,
        tarefa_id: int,
        inicio: datetime,
        fim: datetime,
        duracao_min: int,
        observacao: str | None = None,
    ) -> None:
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pomodoro (tarefa_id, inicio, fim, duracao_min, observacao)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tarefa_id, inicio, fim, duracao_min, observacao),
            )
            conn.commit()
        finally:
            conn.close()

    def obter_totais(self) -> tuple[int, int]:
        """Retorna (soma de duracao_min, total de sessões) considerando todo o histórico."""
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(duracao_min), 0), COUNT(*) FROM pomodoro"
            )
            row = cursor.fetchone()
            return int(row[0] or 0), int(row[1] or 0)
        finally:
            conn.close()

    def contar_sessoes_do_mes(self, referencia: date) -> int:
        """Mantém a mesma comparação por prefixo de string usada no código legado."""
        mes_prefixo = referencia.strftime("%Y-%m")
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM pomodoro WHERE substr(inicio, 1, 7) = ?",
                (mes_prefixo,),
            )
            row = cursor.fetchone()
            return int(row[0] or 0)
        finally:
            conn.close()
