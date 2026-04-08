import time
from datetime import datetime
from backend.database.conexao import registrar_sessao

class PomodoroManager:

    def __init__(self):
        self.tempo_foco = 25 * 60
        self.tempo_pausa = 5 * 60

        self.segundos_restantes = self.tempo_foco
        self.modo_foco = True
        self.rodando = False

        self.inicio_sessao = None

    def iniciar(self):
        if not self.rodando:
            self.rodando = True
            if self.modo_foco:
                self.inicio_sessao = datetime.now()

    def pausar(self):
        self.rodando = False

    def resetar(self):
        self.rodando = False
        self.segundos_restantes = self.tempo_foco if self.modo_foco else self.tempo_pausa

    def atualizar(self):

        if not self.rodando:
            return

        self.segundos_restantes -= 1

        if self.segundos_restantes <= 0:
            self.finalizar_ciclo()

    def finalizar_ciclo(self):

        self.rodando = False

        if self.modo_foco:

            fim = datetime.now()

            registrar_sessao(
                tarefa_id=1,
                inicio=self.inicio_sessao,
                fim=fim,
                observacao="Ciclo Pomodoro completo"
            )

            self.modo_foco = False
            self.segundos_restantes = self.tempo_pausa

        else:

            self.modo_foco = True
            self.segundos_restantes = self.tempo_foco

    def progresso(self):

        total = self.tempo_foco if self.modo_foco else self.tempo_pausa

        return (total - self.segundos_restantes) / total