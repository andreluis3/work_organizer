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

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget#centralWidget {
                background-color: #111111;
            }
            QFrame#sidebar {
                background-color: #1A1A1A;
                border-right: 1px solid #262626;
            }
            QLabel#sidebarBrand {
                color: #F8FBFF;
                font-size: 16px;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton#sidebarButton {
                text-align: left;
                padding: 10px 12px;
                border-radius: 8px;
                color: #C5D2E8;
                background-color: transparent;
                border: none;
                font-size: 13px;
            }
            QPushButton#sidebarButton:hover {
                background-color: #232323;
            }
            QPushButton#sidebarButton:checked {
                background-color: #0078FF;
                color: #FFFFFF;
                font-weight: 600;
            }
            QPushButton#sidebarToggle {
                background-color: #1E2A3F;
                border: none;
                border-radius: 6px;
                color: #C5D2E8;
            }
            QPushButton#sidebarToggle:hover {
                background-color: #2A3954;
            }
            QFrame#topbar {
                background-color: #111111;
                border-bottom: 1px solid #262626;
            }
            QLabel#topbarTitle {
                color: #F8FBFF;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#topbarSubtitle {
                color: #6F819F;
                font-size: 12px;
            }
            QLabel#emptyPlaceholder {
                color: #6F819F;
                font-size: 14px;
            }
            QLabel#pageTitle {
                color: #F8FBFF;
            }

            /* --- QTabWidget (usado na AgendaPage) --- */
            QTabWidget::pane {
                border: 1px solid #262626;
                border-radius: 8px;
                background-color: #1A1A1A;
            }
            QTabBar::tab {
                background-color: #1A1A1A;
                color: #9CB0CF;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #0078FF;
                color: #FFFFFF;
            }

            /* --- Agenda: header e grid --- */
            QLabel#agendaCursorLabel {
                color: #F8FBFF;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#agendaWeekdayHeader {
                color: #9CB0CF;
                font-size: 12px;
                font-weight: 600;
                qproperty-alignment: AlignCenter;
                padding: 6px 0;
            }
            QLabel#agendaHourLabel {
                color: #8CA0C0;
                font-size: 11px;
            }
            QFrame#agendaHourCell {
                background-color: #171717;
                border: 1px solid #262626;
                border-radius: 6px;
            }
            QFrame#agendaHourCell:hover {
                background-color: #1F1F1F;
            }

            /* --- CalendarDayCell --- */
            QFrame#dayCell, QFrame#dayCellOutside, QFrame#dayCellToday {
                border-radius: 8px;
                border: 1px solid #262626;
            }
            QFrame#dayCell {
                background-color: #1A1A1A;
            }
            QFrame#dayCellOutside {
                background-color: #141414;
            }
            QFrame#dayCellToday {
                background-color: #17335C;
                border: 1px solid #0078FF;
            }
            QLabel#dayCellNumber {
                color: #F8FBFF;
                font-weight: 600;
            }
            QLabel#dayCellNumberOutside {
                color: #5A6478;
                font-weight: 600;
            }
            QLabel#dayCellMore {
                color: #8CA0C0;
                font-size: 10px;
            }
            QLabel#eventPill {
                border-radius: 6px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 600;
            }

            /* --- EventDialog --- */
            QDialog {
                background-color: #111111;
            }
            QLabel#dialogTitle {
                color: #F8FBFF;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#sectionLabel {
                color: #D7E3F6;
                font-size: 14px;
                font-weight: 600;
            }
            QFrame#formFrame {
                background-color: #1A1A1A;
                border: 1px solid #262626;
                border-radius: 10px;
            }
            QFrame#eventRow {
                background-color: #1A1A1A;
                border: 1px solid #262626;
                border-radius: 8px;
            }
            QLabel#eventTime {
                color: #38BDF8;
                font-weight: 600;
            }
            QLabel#eventTitle {
                color: #F8FBFF;
                font-weight: 600;
            }
            QLabel#emptyHint {
                color: #8EA2C2;
            }
            QLabel#dialogStatus {
                color: #FF6B6B;
            }
            QPushButton#primaryButton {
                background-color: #22C55E;
                color: #03130B;
                font-weight: 700;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton#primaryButton:hover {
                background-color: #16A34A;
            }
            QPushButton#dangerButton {
                background-color: #7F1D1D;
                color: #FEE2E2;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton#dangerButton:hover {
                background-color: #991B1B;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0D1526;
                border: 1px solid #263449;
                border-radius: 6px;
                padding: 6px 8px;
                color: #F8FBFF;
            }
            QPushButton {
                color: #F8FBFF;
            }
            
            /* --- Dashboard --- */
            QFrame#dashboardCard {
                background-color: #1A1A1A;
                border: 1px solid #262626;
                border-radius: 16px;
            }
            QLabel#dashboardWelcome {
                color: #F8FBFF;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#dashboardSummary {
                color: #94A3B8;
                font-size: 12px;
            }
            QProgressBar#xpBar {
                background-color: #172036;
                border: none;
                border-radius: 6px;
            }
            QProgressBar#xpBar::chunk {
                background-color: #00F5FF;
                border-radius: 6px;
            }
            QLabel#xpCaption {
                color: #00F5FF;
                font-size: 11px;
            }
            QFrame#streakPanel {
                background-color: #1A120A;
                border: 1px solid #7C2D12;
                border-radius: 12px;
            }
            QLabel#streakTitle {
                color: #FDBA74;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#streakValue {
                color: #FB923C;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#streakHint {
                color: #FED7AA;
                font-size: 11px;
            }
            QLabel#dashboardSectionTitle {
                color: #F8FBFF;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#dashboardDynamicMessage {
                color: #00F5FF;
                font-size: 12px;
            }
            QFrame#statCard {
                background-color: #0B1220;
                border: 1px solid #263449;
                border-radius: 12px;
            }
            QLabel#statCardTitle {
                color: #8CA0BE;
                font-size: 12px;
            }
            QLabel#statCardValue {
                color: #F8FBFF;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#statCardSubtitle {
                color: #6F819F;
                font-size: 11px;
            }
            QLabel#goalLabel {
                color: #00F5FF;
                font-size: 13px;
            }
            QLabel#goalPercent {
                color: #22C55E;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#goalPercent[completed="true"] {
                color: #00F5FF;
            }
            QProgressBar#goalBar {
                background-color: #172036;
                border: none;
                border-radius: 7px;
            }
            QProgressBar#goalBar::chunk {
                background-color: #22C55E;
                border-radius: 7px;
            }
            QProgressBar#goalBar[completed="true"]::chunk {
                background-color: #00F5FF;
            }
            QLabel#goalHint {
                color: #94A3B8;
                font-size: 11px;
            }
            QLabel#forestMessage, QLabel#forestEmptyHint {
                color: #94A3B8;
                font-size: 12px;
            }
            QFrame#treeCard {
                background-color: #0E1A16;
                border-radius: 10px;
            }
            QLabel#treeEmoji {
                font-size: 20px;
            }
        
            
            """
            
            
            
            
        )