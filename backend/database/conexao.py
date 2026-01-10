import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database" / "organizador.db"

def conectar():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def registrar_sessao(tarefa_id, inicio, fim, observacao=""):
    duracao = int((fim - inicio).total_seconds() / 60)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pomodoro (tarefa_id, inicio, fim, duracao_min, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (tarefa_id, inicio, fim, duracao, observacao))

    conn.commit()
    conn.close()

def produtividade_por_dia(data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(duracao_min) as total
        FROM pomodoro
        WHERE DATE(inicio) = DATE(?)
    """, (data,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado["total"] or 0