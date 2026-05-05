from backend.database.conexao import conectar

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # TAREFAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        data_inicio DATE,
        data_fim DATE,
        status TEXT DEFAULT 'pendente',
        prioridade INTEGER DEFAULT 3,
        criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # METAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        horas_objetivo INTEGER,
        horas_concluidas INTEGER DEFAULT 0,
        data_inicio DATE,
        data_fim DATE
    )
    """)

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pomodoro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarefa_id INTEGER,
        inicio TIMESTAMP NOT NULL,
        fim TIMESTAMP NOT NULL,
        duracao_min INTEGER NOT NULL,
        observacao TEXT,
        FOREIGN KEY (tarefa_id) REFERENCES tarefas(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME
                            );
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_notes_titulo ON notes(titulo);
    """)
               
    conn.commit()
    conn.close()


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas criadas com sucesso.")
