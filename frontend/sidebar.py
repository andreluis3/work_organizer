from __future__ import annotations

import customtkinter as ctk

from frontend.ui_assets import load_icon


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="#0f172a", corner_radius=0, width=235)

        self.controller = controller
        self.expanded_width = 235
        self.collapsed_width = 74
        self._anim_job = None

        self.grid_propagate(False)
        self.grid_rowconfigure(99, weight=1)

        self.header = ctk.CTkLabel(
            self,
            text="WORKFLOW",
            font=("Segoe UI", 18, "bold"),
            text_color="#f6f8fc",
            anchor="w",
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 16))

        self.toggle_btn = ctk.CTkButton(
            self,
            text="◀",
            width=34,
            height=30,
            corner_radius=8,
            fg_color="#1e2a3f",
            hover_color="#2a3954",
            command=self.controller.toggle_sidebar,
        )
        self.toggle_btn.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(18, 16))

        self._buttons: dict[str, ctk.CTkButton] = {}
        self._labels: dict[str, str] = {}

        items = [
            ("dashboard", "Dashboard", "home.png"),
            ("agenda", "Agenda", "calendar.png"),
            ("cursos", "Cursos", "task.png"),
            ("academia", "Academia", "leaf.png"),
            ("configuracoes", "Configurações", "task.png"),
        ]

        for row, (key, label, icon_name) in enumerate(items, start=1):
            btn = ctk.CTkButton(
                self,
                text=label,
                image=load_icon(icon_name),
                compound="left",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#1a2740",
                text_color="#c5d2e8",
                command=lambda name=key: self.controller.show_screen(name),
            )
            btn.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
            self._buttons[key] = btn
            self._labels[key] = label

        self.grid_columnconfigure(0, weight=1)

    def set_active(self, screen_name: str) -> None:
        for key, button in self._buttons.items():
            if key == screen_name:
                button.configure(fg_color="#22395e", text_color="#f8fbff")
            else:
                button.configure(fg_color="transparent", text_color="#c5d2e8")

    def set_collapsed(self, collapsed: bool) -> None:
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)

        target_width = self.collapsed_width if collapsed else self.expanded_width
        self._animate_width(target_width)
        self.toggle_btn.configure(text="▶" if collapsed else "◀")

        if collapsed:
            self.header.configure(text="WF", anchor="center")
            for key, button in self._buttons.items():
                button.configure(text="", anchor="center")
        else:
            self.header.configure(text="WORKFLOW", anchor="w")
            for key, button in self._buttons.items():
                button.configure(text=self._labels[key], anchor="w")

    

    def _animate_width(self, target_width: int) -> None:
        current_width = self.winfo_width()
        if current_width <= 1:
            current_width = self.expanded_width

        if abs(current_width - target_width) <= 3:
            self.configure(width=target_width)
            return

        step = 12 if target_width > current_width else -12
        self.configure(width=current_width + step)
        self._anim_job = self.after(12, lambda: self._animate_width(target_width))
