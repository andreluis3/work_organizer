from __future__ import annotations

import customtkinter as ctk


class BaseScreen(ctk.CTkFrame):
    title = "Tela"

    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.title,
            font=("Segoe UI", 28, "bold"),
            text_color="#f8fbff",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew")

        self._intro_step = 0

    def on_show(self) -> None:
        self._intro_step = 0
        self._animate_intro()

    def _animate_intro(self) -> None:
        self._intro_step += 1
        pady = max(0, 16 - (self._intro_step * 3))
        self.content.grid_configure(pady=(pady, 0))
        if self._intro_step < 6:
            self.after(16, self._animate_intro)
