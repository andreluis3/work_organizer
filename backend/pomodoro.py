# core/crud.py
from database.conexao import conectar

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
