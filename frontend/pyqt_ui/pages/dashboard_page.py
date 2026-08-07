"""
Página do Dashboard: orquestra o ViewModel e os widgets de cada seção.

Não contém regra de negócio nem formatação — apenas monta o layout e
repassa os DTOs do DashboardViewModel para os widgets corretos.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QGridLayout, QWidget

from frontend.pyqt_ui.pages.base_page import BasePage
from frontend.pyqt_ui.viewmodels.dashboard_viewmodel import DashboardViewModel
from frontend.pyqt_ui.widgets.dashboard.dashboard_charts import DashboardChartsWidget
from frontend.pyqt_ui.widgets.dashboard.dashboard_forest import DashboardForestWidget
from frontend.pyqt_ui.widgets.dashboard.dashboard_goal import DashboardGoalWidget
from frontend.pyqt_ui.widgets.dashboard.dashboard_header import DashboardHeaderWidget
from frontend.pyqt_ui.widgets.dashboard.dashboard_hero import DashboardHeroWidget


class DashboardPage(BasePage):
    title = "Dashboard"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.viewmodel = DashboardViewModel()
        self.viewmodel.updated.connect(self._apply_viewmodel)

        grid_container = QWidget()
        grid = QGridLayout(grid_container)
        grid.setSpacing(16)
        for col in range(3):
            grid.setColumnStretch(col, 1)

        self.header_widget = DashboardHeaderWidget()
        grid.addWidget(self.header_widget, 0, 0, 1, 3)

        self.hero_widget = DashboardHeroWidget()
        grid.addWidget(self.hero_widget, 1, 0, 1, 3)

        self.charts_widget = DashboardChartsWidget()
        grid.addWidget(self.charts_widget, 2, 0, 1, 3)

        self.goal_widget = DashboardGoalWidget()
        grid.addWidget(self.goal_widget, 3, 0, 1, 2)

        self.forest_widget = DashboardForestWidget()
        grid.addWidget(self.forest_widget, 3, 2, 1, 1)

        self.add_content_widget(grid_container)

    def on_show(self) -> None:
        super().on_show()
        self.viewmodel.refresh()

    def _apply_viewmodel(self) -> None:
        self.header_widget.update_data(self.viewmodel.header)
        self.hero_widget.update_data(self.viewmodel.hero)
        self.goal_widget.update_data(self.viewmodel.goal)
        self.forest_widget.update_data(self.viewmodel.forest)
        self.charts_widget.update_data(self.viewmodel.charts)