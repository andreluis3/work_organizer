"""
Gráficos do Dashboard: foco em minutos (linha) e sessões por dia (barra),
últimos 7 dias. Usa QtCharts (PyQt6-Charts).

Widget burro: recebe listas já prontas via ChartsViewData e apenas desenha.
"""

from __future__ import annotations
from frontend.pyqt_ui.pages.dashboard_page import DashboardPage
from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import ChartsViewData

CYAN = QColor("#00F5FF")
ORANGE = QColor("#FB923C")
MUTED = QColor("#94A3B8")



class DashboardChartsWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        self.focus_chart_view = self._build_line_chart_view("Minutos focados")
        self.sessions_chart_view = self._build_bar_chart_view("Sessoes por dia")

        root.addWidget(self.focus_chart_view, stretch=2)
        root.addWidget(self.sessions_chart_view, stretch=1)

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def _build_line_chart_view(self, title: str) -> QChartView:
        self.focus_series = QLineSeries()
        pen = QPen(CYAN)
        pen.setWidth(3)
        self.focus_series.setPen(pen)

        chart = QChart()
        chart.addSeries(self.focus_series)
        chart.setTitle(title)
        chart.legend().hide()
        chart.setBackgroundVisible(False)
        chart.setTitleBrush(MUTED)

        self.focus_axis_x = QBarCategoryAxis()
        self.focus_axis_y = QValueAxis()
        self.focus_axis_y.setLabelFormat("%d")

        chart.addAxis(self.focus_axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(self.focus_axis_y, Qt.AlignmentFlag.AlignLeft)
        self.focus_series.attachAxis(self.focus_axis_x)
        self.focus_series.attachAxis(self.focus_axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return view

    def _build_bar_chart_view(self, title: str) -> QChartView:
        self.sessions_bar_set = QBarSet("Sessoes")
        self.sessions_bar_set.setColor(ORANGE)

        series = QBarSeries()
        series.append(self.sessions_bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.legend().hide()
        chart.setBackgroundVisible(False)
        chart.setTitleBrush(MUTED)

        self.sessions_axis_x = QBarCategoryAxis()
        self.sessions_axis_y = QValueAxis()
        self.sessions_axis_y.setLabelFormat("%d")

        chart.addAxis(self.sessions_axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(self.sessions_axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.sessions_axis_x)
        series.attachAxis(self.sessions_axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return view

    # ------------------------------------------------------------------
    # Atualização de dados
    # ------------------------------------------------------------------

    def update_data(self, data: ChartsViewData) -> None:
        self._update_line_chart(data.week_labels, data.week_minutes)
        self._update_bar_chart(data.week_labels, data.week_sessions)

    def _update_line_chart(self, labels: list[str], values: list[int]) -> None:
        self.focus_series.clear()
        for index, value in enumerate(values):
            self.focus_series.append(float(index), float(value))

        self.focus_axis_x.clear()
        self.focus_axis_x.append(labels)

        max_value = max(values) if values else 1
        self.focus_axis_y.setRange(0, max(1, max_value) * 1.2)

    def _update_bar_chart(self, labels: list[str], values: list[int]) -> None:
        self.sessions_bar_set.remove(0, self.sessions_bar_set.count())
        for value in values:
            self.sessions_bar_set.append(value)

        self.sessions_axis_x.clear()
        self.sessions_axis_x.append(labels)

        max_value = max(values) if values else 1
        self.sessions_axis_y.setRange(0, max(1, max_value) * 1.2)
     