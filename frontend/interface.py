from __future__ import annotations

import customtkinter as ctk

from frontend.app_controller import AppController
from frontend.sidebar import Sidebar
from frontend.telas import (
    AgendaScreen,
    ConfiguracoesScreen,
    CursosScreen,
    DashboardScreen,
    FocusScreen,
    NotesScreen,
    TasksPage,
)

ctk.set_default_color_theme("blue")


class App(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.controller = AppController(self)
        ctk.set_appearance_mode(self.controller.state.theme)

        # 🔥 CORREÇÃO: remove coisas de janela
        self.configure(fg_color="#04070f")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, controller=self.controller)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.controller.register_sidebar(self.sidebar)

        self.container = ctk.CTkFrame(self, fg_color="#050c18", corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._build_screens()

    def _build_screens(self) -> None:
        screens = {
            "dashboard": DashboardScreen(self.container, self.controller),
            "tasks": TasksPage(self.container, self.controller),
            "agenda": AgendaScreen(self.container, self.controller),
            "notes": NotesScreen(self.container, self.controller),
            "focus": FocusScreen(self.container, self.controller),
            "settings": ConfiguracoesScreen(self.container, self.controller),

            # aliases
            "focustime": FocusScreen(self.container, self.controller),
            "cursos": CursosScreen(self.container, self.controller),
            "configuracoes": ConfiguracoesScreen(self.container, self.controller),
        }

        for name, screen in screens.items():
            self.controller.register_screen(name, screen)

        self.controller.show_screen("dashboard")