# frontend/pyqt_ui/main_window.py
"""
Janela principal da aplicação PyQt6.

Monta o casco visual (Sidebar + TopBar + área de páginas) e o sistema de
navegação. Não contém regra de negócio: apenas orquestra qual página fica
visível no QStackedWidget.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from frontend.app_state import AppState
from frontend.config.settings import SettingsStore
from frontend.pyqt_ui.widgets.sidebar import Sidebar
from frontend.pyqt_ui.widgets.topbar import TopBar


class MainWindow(QMainWindow):
    def __init__(
        self,
        app_state: AppState,
        settings_store: SettingsStore,
        controllers: dict,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.app_state = app_state
        self.settings_store = settings_store
        self.controllers = controllers

        self._page_indexes: dict[str, int] = {}
        self._page_labels: dict[str, str] = {}

        self.setWindowTitle("Organizador de Trabalho")
        self.resize(1240, 760)
        self.setMinimumSize(1100, 680)

        self._build_ui()
        self._apply_theme()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar(start_collapsed=self.app_state.sidebar_collapsed)
        self.sidebar.navigation_requested.connect(self.show_page)
        self.sidebar.collapsed_changed.connect(self._on_sidebar_collapsed_changed)
        root_layout.addWidget(self.sidebar)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.topbar = TopBar()
        right_layout.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.stack)

        root_layout.addWidget(right_column, stretch=1)

        empty_placeholder = QLabel("Selecione uma página no menu lateral.")
        empty_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_placeholder.setObjectName("emptyPlaceholder")
        self.stack.addWidget(empty_placeholder)

    # ------------------------------------------------------------------
    # Sistema de navegação
    # ------------------------------------------------------------------

    def register_page(self, key: str, label: str, page: QWidget) -> None:
        index = self.stack.addWidget(page)
        self._page_indexes[key] = index
        self._page_labels[key] = label

    def show_page(self, key: str) -> None:
        index = self._page_indexes.get(key)
        if index is None:
            return

        self.stack.setCurrentIndex(index)
        self.sidebar.set_active(key)
        self.topbar.set_title(self._page_labels.get(key, key.title()))
        self.app_state.current_screen = key

        page = self.stack.widget(index)
        on_show = getattr(page, "on_show", None)
        if callable(on_show):
            on_show()

    def _on_sidebar_collapsed_changed(self, collapsed: bool) -> None:
        self.app_state.sidebar_collapsed = collapsed

    # ------------------------------------------------------------------
    # Tema
    # ------------------------------------------------------------------
