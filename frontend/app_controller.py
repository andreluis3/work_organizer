from __future__ import annotations

import customtkinter as ctk

from frontend.app_state import AppState
from frontend.config.settings import AppSettings, SettingsStore
from frontend.widgets.toast import ToastManager


class AppController:
    def __init__(self, app: ctk.CTk):
        self.app = app
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.state = AppState(theme=self.settings.theme)
        self.toast_manager = ToastManager(app)

        self.screens: dict[str, ctk.CTkFrame] = {}
        self.sidebar = None

    def register_sidebar(self, sidebar) -> None:
        self.sidebar = sidebar

    def register_screen(self, name: str, screen: ctk.CTkFrame) -> None:
        self.screens[name] = screen

    def show_screen(self, name: str) -> None:
        if name not in self.screens:
            return

        if self.state.current_screen in self.screens:
            self.screens[self.state.current_screen].grid_remove()

        target = self.screens[name]
        target.grid(row=0, column=0, sticky="nsew")
        self.state.current_screen = name

        if self.sidebar:
            self.sidebar.set_active(name)

        if hasattr(target, "on_show"):
            target.on_show()

    def toast(self, message: str, level: str = "info") -> None:
        if self.state.notifications_enabled:
            self.toast_manager.show(message, level=level)

    def toggle_sidebar(self) -> None:
        self.state.sidebar_collapsed = not self.state.sidebar_collapsed
        if self.sidebar:
            self.sidebar.set_collapsed(self.state.sidebar_collapsed)

    def set_theme(self, theme: str) -> None:
        self.state.theme = theme
        ctk.set_appearance_mode(theme)

        self.settings = AppSettings(theme=theme, accent=self.settings.accent)
        self.settings_store.save(self.settings)

        self.toast(
            f"Tema {('claro' if theme == 'light' else 'escuro')} aplicado e salvo.",
            level="success",
        )
