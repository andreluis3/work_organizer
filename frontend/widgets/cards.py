from __future__ import annotations

import customtkinter as ctk

from frontend.widgets.anim import blend_color


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str = "--", subtitle: str = "", icon: str = "", **kwargs):
        super().__init__(
            master,
            fg_color="#0b1220",
            border_color="#263449",
            border_width=1,
            **kwargs,
        )

        self.title = ctk.CTkLabel(self, text=title, font=("Segoe UI", 14), text_color="#8ca0be")
        self.title.pack(anchor="w", padx=16, pady=(14, 6))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16)
        row.grid_columnconfigure(0, weight=1)

        value_text = f"{icon} {value}".strip()
        self.value_label = ctk.CTkLabel(row, text=value_text, font=("Segoe UI", 24, "bold"), text_color="#f8fbff")
        self.value_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color="#6f819f",
        )
        self.subtitle_label.pack(anchor="w", padx=16, pady=(5, 14))

        self._hover_anim_job = None
        self._hover_progress = 0.0
        self.bind("<Enter>", lambda _: self._animate_hover(True))
        self.bind("<Leave>", lambda _: self._animate_hover(False))
        for child in self.winfo_children():
            child.bind("<Enter>", lambda _: self._animate_hover(True))
            child.bind("<Leave>", lambda _: self._animate_hover(False))

    def set_value(self, value: str, icon: str = "") -> None:
        self.value_label.configure(text=f"{icon} {value}".strip())

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_label.configure(text=subtitle)

    def _animate_hover(self, active: bool) -> None:
        target = 1.0 if active else 0.0
        if self._hover_anim_job is not None:
            self.after_cancel(self._hover_anim_job)
        self._step_hover(target)

    def _step_hover(self, target: float) -> None:
        delta = 0.2 if target > self._hover_progress else -0.2
        self._hover_progress = max(0.0, min(1.0, self._hover_progress + delta))

        border = blend_color("#263449", "#4cc9f0", self._hover_progress)
        bg = blend_color("#0b1220", "#112038", self._hover_progress)
        self.configure(border_color=border, fg_color=bg)

        if abs(self._hover_progress - target) > 0.01:
            self._hover_anim_job = self.after(16, lambda: self._step_hover(target))
        else:
            self._hover_anim_job = None
