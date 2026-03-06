import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "organizador.db"

def conectar():
    # cria pasta database se não existir
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn 



def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # ---------------------------
    # Tabela de sessões Pomodoro
    # ---------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pomodoro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarefa_id INTEGER,
        inicio DATETIME NOT NULL,
        fim DATETIME NOT NULL,
        duracao_min INTEGER NOT NULL,
        observacao TEXT
    )
    """)

    # ---------------------------
    # Tabela de progresso usuário
    # (XP de foco)
    # ---------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progresso_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        minutos_foco INTEGER DEFAULT 0,
        ciclos_completos INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0
    )
    """)

    # ---------------------------
    # Tabela futura de tarefas
    # (integração planner)
    # ---------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        prioridade TEXT,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def registrar_sessao(tarefa_id, inicio, fim, observacao=None):
    conn = conectar()
    cursor = conn.cursor()

    duracao = int((fim - inicio).total_seconds() / 60)

    cursor.execute("""
        INSERT INTO pomodoro (
            tarefa_id,
            inicio,
            fim,
            duracao_min,
            observacao
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        tarefa_id,
        inicio,
        fim,
        duracao,
        observacao
    ))

    conn.commit()
    conn.close()
