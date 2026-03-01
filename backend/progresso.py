# core/progresso.py
from database.conexao import conectar

def produtividade_por_dia(data):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(duracao_min) AS total
        FROM pomodoro
        WHERE DATE(inicio) = DATE(?)
    """, (data,))

    resultado = cursor.fetchone()
    conn.close()

    return resultado["total"] or 0
