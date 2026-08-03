# frontend/pyqt_ui/pages/base_page.py
"""
Página base para toda a interface PyQt6.

Equivalente ao antigo frontend/telas/base_screen.py (CustomTkinter).
Fornece apenas estrutura visual: header com título, área de conteúdo
e animação de entrada. Nenhuma regra de negócio deve viver aqui —
cada página concreta (DashboardPage, TasksPage, ...) é responsável
por consumir seus próprios controllers.
"""

from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class BasePage(QWidget):
    """
    Classe base para todas as páginas (DashboardPage, TasksPage, AgendaPage...).

    Subclasses devem:
    - definir `title` como atributo de classe, e/ou chamar `set_title()`;
    - adicionar seus próprios widgets em `self.content` (via `self.content.layout().addWidget(...)`
      ou pelo helper `add_content_widget()`);
    - sobrescrever `on_show()` quando precisarem recarregar dados, sempre
      chamando `super().on_show()` primeiro para manter a animação de entrada.
    """

    title: str = "Página"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._build_layout()
        self._setup_intro_animation()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 24, 32, 24)
        root_layout.setSpacing(20)

        # --- Header ---
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("pageTitle")
        self.title_label.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #F8FBFF;"
        )
        header_layout.addWidget(self.title_label)

        root_layout.addWidget(header)

        # --- Content: área onde as páginas filhas adicionam seus widgets ---
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        root_layout.addWidget(self.content, stretch=1)

    def add_content_widget(self, widget: QWidget) -> None:
        """Helper para páginas filhas adicionarem componentes ao content."""
        self.content_layout.addWidget(widget)

    def set_title(self, title: str) -> None:
        """Permite trocar o título dinamicamente, se necessário."""
        self.title = title
        self.title_label.setText(title)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_show(self) -> None:
        """
        Chamado pela MainWindow sempre que essa página se torna visível.

        Subclasses devem sobrescrever para recarregar dados (equivalente ao
        antigo BaseScreen.on_show() + refresh() das telas Tkinter), sempre
        chamando super().on_show() para disparar a animação de entrada.
        """
        self._play_intro_animation()

    # ------------------------------------------------------------------
    # Animação de entrada (equivalente ao _animate_intro do CustomTkinter)
    # ------------------------------------------------------------------

    def _setup_intro_animation(self) -> None:
        self._opacity_effect = QGraphicsOpacityEffect(self.content)
        self.content.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        self._intro_animation = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._intro_animation.setDuration(250)
        self._intro_animation.setStartValue(0.0)
        self._intro_animation.setEndValue(1.0)
        self._intro_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _play_intro_animation(self) -> None:
        # Reinicia do zero toda vez que a página é exibida.
        self._intro_animation.stop()
        self._opacity_effect.setOpacity(0.0)
        self._intro_animation.start()