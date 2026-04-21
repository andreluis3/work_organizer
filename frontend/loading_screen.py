import customtkinter as ctk
from frontend.theme import COLORS

class LoadingScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg_main"])

        self.pack(fill="both", expand=True)

        self.label = ctk.CTkLabel(
            self,
            text="Carregando...",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_main"]
        )
        self.label.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(padx=40, pady=10, fill="x")

        self.animate()

    def animate(self):
        self.progress.start()