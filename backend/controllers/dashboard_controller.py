# backend/controllers/dashboard_controller.py
"""
Fachada fina entre a UI e o DashboardService.

Segue o mesmo padrão do TaskController: nenhuma regra de negócio aqui,
apenas repasse. Existe para manter consistência arquitetural (a UI sempre
fala com um Controller, nunca diretamente com Services) e como ponto único
de expansão futura (cache, logging, etc.) sem tocar na UI.
"""

from __future__ import annotations

from backend.services.dashboard_service import DashboardService, DashboardSnapshot


class DashboardController:
    def __init__(self, service: DashboardService | None = None) -> None:
        self.service = service or DashboardService()

    def get_snapshot(self) -> DashboardSnapshot:
        return self.service.get_snapshot()

    def get_dynamic_message(self, snapshot: DashboardSnapshot) -> str:
        return self.service.get_dynamic_message(snapshot)