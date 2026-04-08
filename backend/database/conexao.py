import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "organizador.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def inicializar_banco():

    conn = conectar()
    cursor = conn.cursor()

    # -----------------------------
    # Tabela de notas
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT UNIQUE,
        conteudo TEXT,
        data_criacao DATETIME,
        data_atualizacao DATETIME
    )
    """)

    # -----------------------------
    # Pomodoro
    # -----------------------------
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

    # -----------------------------
    # Progresso usuário
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progresso_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        minutos_foco INTEGER DEFAULT 0,
        ciclos_completos INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0
    )
    """)

    # -----------------------------
    # Tarefas
    # -----------------------------
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


# -----------------------------
# Registrar sessão pomodoro
# -----------------------------
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

    print(f"[DEBUG] Sessão Pomodoro registrada | duração: {duracao} min")

    conn.commit()
    conn.close()