import customtkinter as ctk
import threading

from frontend.loading_screen import LoadingScreen
from frontend.interface import App


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Work Organizer")
        self.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Loading
        self.loading = LoadingScreen(self)

        # Thread para carregar
        threading.Thread(target=self._load_app, daemon=True).start()

    def _load_app(self):
        import time
        time.sleep(1.5)  # simulação

        self.after(0, self._start_app)

    def _start_app(self):
        self.loading.destroy()

        self.app = App(self)  # App agora precisa ser CTkFrame
        self.app.pack(fill="both", expand=True)
        self.title("Organizador de Trabalho")
        self.geometry("1240x760")
        self.minsize(1100, 680)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()