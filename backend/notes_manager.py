from datetime import datetime
from backend.database.conexao import conectar


class NotesManager:

    def __init__(self):
        self.conn = conectar()
        self.cursor = self.conn.cursor()

    # -----------------------------
    # Verifica se já existe título
    # -----------------------------
    def titulo_existe(self, titulo, ignore_id=None):

        if ignore_id:
            self.cursor.execute("""
                SELECT id FROM notes
                WHERE titulo = ? AND id != ?
            """, (titulo, ignore_id))
        else:
            self.cursor.execute("""
                SELECT id FROM notes
                WHERE titulo = ?
            """, (titulo,))

        return self.cursor.fetchone() is not None

    # -----------------------------
    # Criar nova nota
    # -----------------------------
    def criar_nota(self, titulo="Nova Nota", conteudo=""):

        if self.titulo_existe(titulo):
            return None

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
            INSERT INTO notes (
                titulo,
                conteudo,
                data_criacao,
                data_atualizacao
            )
            VALUES (?, ?, ?, ?)
        """, (titulo, conteudo, agora, agora))

        self.conn.commit()

        return self.cursor.lastrowid

    # -----------------------------
    # Atualizar nota
    # -----------------------------
    def atualizar_nota(self, note_id, titulo, conteudo):

        if self.titulo_existe(titulo, note_id):
            return False

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
            UPDATE notes
            SET titulo = ?, conteudo = ?, data_atualizacao = ?
            WHERE id = ?
        """, (titulo, conteudo, agora, note_id))

        self.conn.commit()

        return True

    # -----------------------------
    # Listar notas
    # -----------------------------
    def listar_notas(self):

        try:
            self.cursor.execute("""
                SELECT id, titulo, data_atualizacao
                FROM notes
                ORDER BY data_atualizacao DESC
            """)
            return self.cursor.fetchall()

        except Exception as e:
            print("Erro ao listar notas:", e)
            return []

    # -----------------------------
    # Buscar notas
    # -----------------------------
    def buscar_notas(self, termo):

        self.cursor.execute("""
            SELECT id, titulo, data_atualizacao
            FROM notes
            WHERE titulo LIKE ?
            ORDER BY data_atualizacao DESC
        """, (f"%{termo}%",))

        return self.cursor.fetchall()

    # -----------------------------
    # Carregar nota
    # -----------------------------
    def carregar_nota(self, note_id):

        self.cursor.execute("""
            SELECT titulo, conteudo
            FROM notes
            WHERE id = ?
        """, (note_id,))

        return self.cursor.fetchone()

    # -----------------------------
    # Deletar nota
    # -----------------------------
    def deletar_nota(self, note_id):

        self.cursor.execute("""
            DELETE FROM notes
            WHERE id = ?
        """, (note_id,))

        self.conn.commit()