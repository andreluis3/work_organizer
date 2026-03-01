from __future__ import annotations

import customtkinter as ctk


TOAST_COLORS = {
    "info": ("#1b314b", "#73b8ff"),
    "success": ("#113223", "#59d18d"),
    "warning": ("#473314", "#ffc260"),
    "error": ("#4a1f27", "#ff7992"),
}


class ToastManager:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.toasts: list[ctk.CTkFrame] = []

    def show(self, message: str, level: str = "info", duration_ms: int = 2400) -> None:
        bg, fg = TOAST_COLORS.get(level, TOAST_COLORS["info"])
        toast = ctk.CTkFrame(self.root, fg_color=bg, corner_radius=10, border_width=1, border_color=fg)

        label = ctk.CTkLabel(
            toast,
            text=message,
            font=("Segoe UI", 13, "bold"),
            text_color="#f9fbff",
            anchor="w",
        )
        label.pack(fill="x", padx=12, pady=8)

        self.toasts.append(toast)
        self._reflow()
        self._animate_in(toast, duration_ms)

    def _reflow(self) -> None:
        start_y = 20
        for index, toast in enumerate(self.toasts):
            toast.place(relx=1.0, x=-18, y=start_y + (index * 54), anchor="ne")

    def _animate_in(self, toast: ctk.CTkFrame, duration_ms: int) -> None:
        state = {"step": 0}

        def tick():
            state["step"] += 1
            y_offset = max(0, 16 - state["step"] * 4)
            toast.place_configure(x=-18, rely=0.0, y=20 + (self.toasts.index(toast) * 54) + y_offset)

            if state["step"] < 4:
                toast.after(16, tick)
            else:
                toast.after(duration_ms, lambda: self._animate_out(toast))

        tick()

    def _animate_out(self, toast: ctk.CTkFrame) -> None:
        state = {"step": 0}

        def tick():
            state["step"] += 1
            toast.place_configure(x=-18 + state["step"] * 8)
            if state["step"] < 5:
                toast.after(16, tick)
                return

            if toast in self.toasts:
                self.toasts.remove(toast)
            toast.destroy()
            self._reflow()

        tick()
