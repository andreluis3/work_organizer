from __future__ import annotations

import customtkinter as ctk


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, on_close):
        super().__init__(master)
        self.on_close = on_close

        self.overrideredirect(True)
        self.geometry("420x260")
        self.configure(fg_color="#0d1727")

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 260) // 2
        self.geometry(f"+{x}+{y}")

        container = ctk.CTkFrame(self, fg_color="#0d1727")
        container.pack(expand=True, fill="both", padx=24, pady=24)

        ctk.CTkLabel(
            container,
            text="Work Organizer",
            font=("Segoe UI", 30, "bold"),
            text_color="#f8fbff",
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            container,
            text="Planejamento, foco e execução",
            font=("Segoe UI", 14),
            text_color="#95a7c4",
        ).pack()

        self.progress = ctk.CTkProgressBar(container, width=280, progress_color="#4cc9f0")
        self.progress.pack(pady=30)
        self.progress.set(0)

        self.after(80, self._animate)

    def _animate(self):
        value = self.progress.get()
        if value < 1:
            self.progress.set(value + 0.04)
            self.after(45, self._animate)
            return
        self.destroy()
        self.on_close()
