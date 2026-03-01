from __future__ import annotations

from datetime import date

from backend.database.conexao import conectar


class MetricsService:
    @staticmethod
    def dashboard_metrics() -> dict[str, str]:
        metrics = {
            "tarefas_hoje": "0",
            "tarefas_pendentes": "0",
            "foco_hoje": "0 min",
            "produtividade": "0%",
        }

        try:
            conn = conectar()
            cursor = conn.cursor()

            today = date.today().isoformat()

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM tarefas
                WHERE DATE(COALESCE(data_fim, criada_em)) = DATE(?)
                """,
                (today,),
            )
            metrics["tarefas_hoje"] = str(cursor.fetchone()["total"])

            cursor.execute("SELECT COUNT(*) AS total FROM tarefas WHERE status != 'concluida'")
            pendentes = cursor.fetchone()["total"]
            metrics["tarefas_pendentes"] = str(pendentes)

            cursor.execute(
                """
                SELECT COALESCE(SUM(duracao_min), 0) AS total
                FROM pomodoro
                WHERE DATE(inicio) = DATE(?)
                """,
                (today,),
            )
            focus_minutes = int(cursor.fetchone()["total"])
            metrics["foco_hoje"] = f"{focus_minutes} min"

            concluido = max(0, int(metrics["tarefas_hoje"]) - pendentes)
            total = max(1, int(metrics["tarefas_hoje"]))
            metrics["produtividade"] = f"{int((concluido / total) * 100)}%"

            conn.close()
        except Exception:
            pass

        return metrics
