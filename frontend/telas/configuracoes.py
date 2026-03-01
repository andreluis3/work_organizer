from __future__ import annotations

import customtkinter as ctk

from frontend.telas.base_screen import BaseScreen


class ConfiguracoesScreen(BaseScreen):
    title = "Configurações"

    def __init__(self, master, controller):
        super().__init__(master, controller)

        box = ctk.CTkFrame(self.content, fg_color="#0b1220", corner_radius=14)
        box.pack(fill="x", pady=6)

        ctk.CTkLabel(
            box,
            text="Tema da interface",
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.theme_switch = ctk.CTkSwitch(
            box,
            text="Modo claro",
            command=self._toggle_theme,
        )
        self.theme_switch.pack(anchor="w", padx=16, pady=(0, 14))

    def on_show(self) -> None:
        super().on_show()
        if self.controller.state.theme == "light":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

    def _toggle_theme(self) -> None:
        selected = "light" if self.theme_switch.get() else "dark"
        self.controller.set_theme(selected)
