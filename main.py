from frontend.interface import App
from frontend.telas import SplashScreen
from backend.database.conexao import conectar, inicializar_banco


def main() -> None:


    def open_app() -> None:
        app.deiconify()

    SplashScreen(app, on_close=open_app)
    app.mainloop()
    

if __name__ == "__main__":
    inicializar_banco()

    app = App()
    app.mainloop()
