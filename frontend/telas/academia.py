from __future__ import annotations

import customtkinter as ctk

from frontend.telas.base_screen import BaseScreen


class AcademiaScreen(BaseScreen):
    title = "Academia"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(
            self.content,
            text="Treinos da semana e consistência.",
            font=("Segoe UI", 16),
            text_color="#9cb0cf",
        ).pack(anchor="w")
