from database.conexao import conectar
from datetime import date


def criar_tarefa(
    titulo: str,
    descricao: str = "",
    data_inicio: date | None = None,
    data_fim: date | None = None,
    prioridade: int = 3
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tarefas (
            titulo, descricao, data_inicio, data_fim, prioridade
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        titulo,
        descricao,
        data_inicio,
        data_fim,
        prioridade
    ))

    conn.commit()
    conn.close()


# ---------- LER ----------
def listar_tarefas(filtro_status: str | None = None):
    conn = conectar()
    cursor = conn.cursor()

    if filtro_status:
        cursor.execute("""
            SELECT * FROM tarefas
            WHERE status = ?
            ORDER BY prioridade ASC, data_fim ASC
        """, (filtro_status,))
    else:
        cursor.execute("""
            SELECT * FROM tarefas
            ORDER BY prioridade ASC, data_fim ASC
        """)

    tarefas = cursor.fetchall()
    conn.close()
    return tarefas


def buscar_tarefa_por_id(tarefa_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM tarefas WHERE id = ?
    """, (tarefa_id,))

    tarefa = cursor.fetchone()
    conn.close()
    return tarefa


# ---------- ATUALIZAR ----------
def atualizar_tarefa(
    tarefa_id: int,
    titulo: str,
    descricao: str,
    data_inicio,
    data_fim,
    prioridade: int
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tarefas
        SET titulo = ?, descricao = ?, data_inicio = ?, data_fim = ?, prioridade = ?
        WHERE id = ?
    """, (
        titulo,
        descricao,
        data_inicio,
        data_fim,
        prioridade,
        tarefa_id
    ))

    conn.commit()
    conn.close()


def atualizar_status(tarefa_id: int, status: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tarefas
        SET status = ?
        WHERE id = ?
    """, (status, tarefa_id))

    conn.commit()
    conn.close()


# ---------- DELETAR ----------
def deletar_tarefa(tarefa_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tarefas WHERE id = ?
    """, (tarefa_id,))

    conn.commit()
    conn.close()
