from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class TimerRingWidget(QWidget):
    """Anel de progresso circular com o tempo restante no centro.

    "Burro": só desenha o que `update_data()` manda, nenhuma lógica de timer.
    """

    TRACK_COLOR = QColor("#102434")
    PROGRESS_COLOR_RUNNING = QColor("#00F5FF")
    PROGRESS_COLOR_PAUSED = QColor("#5f8890")
    TEXT_COLOR = QColor("#EFFFFF")
    RING_WIDTH = 14

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self._progress = 0.0
        self._timer_text = "25:00"
        self._is_running = False
        self._is_paused = False

    def update_data(self, timer_text: str, progress: float, is_running: bool, is_paused: bool) -> None:
        self._timer_text = timer_text
        self._progress = max(0.0, min(1.0, progress))
        self._is_running = is_running
        self._is_paused = is_paused
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - assinatura Qt
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height()) - self.RING_WIDTH - 10
        rect = QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side,
        )

        track_pen = QPen(self.TRACK_COLOR, self.RING_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        color = self.PROGRESS_COLOR_PAUSED if self._is_paused else self.PROGRESS_COLOR_RUNNING
        progress_pen = QPen(color, self.RING_WIDTH, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        span_angle = int(-360 * 16 * self._progress)
        painter.drawArc(rect, 90 * 16, span_angle)

        painter.setPen(QPen(self.TEXT_COLOR))
        painter.setFont(QFont("Consolas", 42, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._timer_text)
