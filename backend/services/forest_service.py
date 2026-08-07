# backend/services/forest_service.py
"""
Regra de negócio da "floresta de foco".

Cada sessão de pomodoro concluída planta uma árvore. A mensagem de status
varia conforme o tamanho da floresta. Serviço puro: sem SQL, sem UI,
totalmente testável com um inteiro de entrada.

Migração 1:1 de frontend/telas/forest_system.py, sem mudança de
comportamento — apenas sem estado mutável.
"""

from __future__ import annotations

from dataclasses import dataclass

TREE_EMOJI = "🌲"


@dataclass(frozen=True, slots=True)
class ForestSnapshot:
    trees: list[str]
    message: str

    @property
    def total(self) -> int:
        return len(self.trees)


class ForestService:
    def build(self, total_sessions: int) -> ForestSnapshot:
        """Monta a floresta a partir do total de sessões concluídas."""
        count = max(0, total_sessions)
        trees = [TREE_EMOJI] * count
        message = self._resolve_message(count)
        return ForestSnapshot(trees=trees, message=message)

    def _resolve_message(self, total: int) -> str:
        if total == 0:
            return "Plante sua primeira árvore."
        if total < 3:
            return "Sua floresta está começando..."
        if total < 10:
            return "Sua floresta está crescendo 🌱"
        return "Sua floresta está prosperando 🌳"