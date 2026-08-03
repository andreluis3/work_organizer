# frontend/pyqt_ui/widgets/sidebar.py
"""
Sidebar reutilizável da nova interface PyQt6.

Migração do frontend/telas/sidebar.py (CustomTkinter). Não conhece
MainWindow, QStackedWidget nem AppState — apenas emite sinais.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

# frontend/pyqt_ui/widgets/sidebar.py -> frontend/assets/icons
ICON_DIR = Path(__file__).resolve().parents[2] / "assets" / "icons"

# (chave interna, rótulo exibido, arquivo do ícone)
NAV_ITEMS = [
    ("dashboard", "Dashboard", "home.png"),
    ("tasks", "Tasks", "task.png"),
    ("agenda", "Agenda", "calendar.png"),
    ("notes", "Notes", "leaf.png"),
    ("focus", "Focus", "png1.png"),
    ("settings", "Configurações", "png2.png"),
]


def _load_icon(filename: str) -> QIcon:
    path = ICON_DIR / filename
    if not path.exists():
        return QIcon()
    return QIcon(str(path))


class Sidebar(QFrame):
    """Sidebar colapsável. Comunica-se com o resto do app apenas via sinais."""

    navigation_requested = pyqtSignal(str)
    collapsed_changed = pyqtSignal(bool)

    EXPANDED_WIDTH = 235
    COLLAPSED_WIDTH = 74
    ANIMATION_MS = 220

    def __init__(self, start_collapsed: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")

        self._collapsed = False
        self._buttons: dict[str, QPushButton] = {}
        self._labels: dict[str, str] = {}

        self.setMinimumWidth(0)
        self.setMaximumWidth(self.EXPANDED_WIDTH)

        self._build_ui()

        self._animation = QPropertyAnimation(self, b"maximumWidth", self)
        self._animation.setDuration(self.ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if start_collapsed:
            self._collapsed = True
            self.setMaximumWidth(self.COLLAPSED_WIDTH)
            self._apply_collapsed_labels(True)
            self.toggle_btn.setText("▶")

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(4)

        self.brand_label = QLabel("WORKFLOW")
        self.brand_label.setObjectName("sidebarBrand")
        layout.addWidget(self.brand_label)

        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setObjectName("sidebarToggle")
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_collapse)
        layout.addWidget(self.toggle_btn)
        layout.addSpacing(12)

        for key, label, icon_filename in NAV_ITEMS:
            button = QPushButton(label)
            button.setObjectName("sidebarButton")
            button.setIcon(_load_icon(icon_filename))
            button.setIconSize(QSize(18, 18))
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked, k=key: self.navigation_requested.emit(k))
            layout.addWidget(button)

            self._buttons[key] = button
            self._labels[key] = label

        layout.addStretch(1)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active(self, key: str) -> None:
        for item_key, button in self._buttons.items():
            button.setChecked(item_key == key)

    def is_collapsed(self) -> bool:
        return self._collapsed

    # ------------------------------------------------------------------
    # Collapse / expand
    # ------------------------------------------------------------------

    def _toggle_collapse(self) -> None:
        self._collapsed = not self._collapsed
        target_width = self.COLLAPSED_WIDTH if self._collapsed else self.EXPANDED_WIDTH

        self._apply_collapsed_labels(self._collapsed)
        self.toggle_btn.setText("▶" if self._collapsed else "◀")

        self._animation.stop()
        self._animation.setStartValue(self.maximumWidth())
        self._animation.setEndValue(target_width)
        self._animation.start()

        self.collapsed_changed.emit(self._collapsed)

    def _apply_collapsed_labels(self, collapsed: bool) -> None:
        if collapsed:
            self.brand_label.setText("WF")
            for key, button in self._buttons.items():
                button.setText("")
                button.setToolTip(self._labels[key])
        else:
            self.brand_label.setText("WORKFLOW")
            for key, button in self._buttons.items():
                button.setText(self._labels[key])
                button.setToolTip("")