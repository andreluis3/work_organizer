from frontend.interface import App
from frontend.telas import SplashScreen


def main() -> None:
    app = App()
    app.withdraw()

    def open_app() -> None:
        app.deiconify()

    SplashScreen(app, on_close=open_app)
    app.mainloop()


if __name__ == "__main__":
    main()
