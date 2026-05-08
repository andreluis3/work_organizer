from backend.database.conexao import conectar

def produtividade_por_dia(data):
    conn = conectar()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(duracao_min), 0) AS total
            FROM pomodoro
            WHERE DATE(inicio) = DATE(?)
        """, (data,))

        resultado = cursor.fetchone()
        return int(resultado["total"] or 0) if resultado else 0
    finally:
        conn.close()
