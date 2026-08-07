"""
Ponto de entrada da aplicação PyQt6.

Responsabilidade única: montar as dependências (settings, state, controllers)
e abrir a janela principal. Nenhuma regra de negócio ou UI é construída aqui.
"""

from __future__ import annotations

import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from backend.controllers.task_controller import TaskController
from frontend.app_state import AppState
from frontend.config.settings import SettingsStore
from frontend.pyqt_ui.main_window import MainWindow
from frontend.pyqt_ui.pages.agenda_page import AgendaPage
from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.pages.dashboard_page import DashboardPage

# Páginas ainda não migradas ganham um placeholder — evita tela em branco
# e permite validar a navegação enquanto migramos uma por vez.
PLACEHOLDER_PAGES = [
    ("tasks", "Tasks"),
    ("notes", "Notes"),
    ("focus", "Focus"),
    ("settings", "Configurações"),
]


def _configure_app_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))


def _build_controllers() -> dict:
    return {
        "task_controller": TaskController(),
    }


def _register_pages(window: MainWindow) -> None:
    for key, label in PLACEHOLDER_PAGES:
        page = BasePage()
        page.set_title(label)
        window.register_page(key, label, page)

    window.register_page("agenda", "Agenda", AgendaPage())
    window.register_page("dashboard", "Dashboard", DashboardPage())


def main() -> int:
    app = QApplication(sys.argv)
    _configure_app_style(app)

    settings_store = SettingsStore()
    settings = settings_store.load()

    app_state = AppState(theme=settings.theme)

    controllers = _build_controllers()

    window = MainWindow(
        app_state=app_state,
        settings_store=settings_store,
        controllers=controllers,
    )
    _register_pages(window)
    window.show_page("dashboard")

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())