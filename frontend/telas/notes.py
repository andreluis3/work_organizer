from __future__ import annotations

from frontend.telas.base_screen import BaseScreen
from notes.notes_ui import NotesUI


class NotesScreen(BaseScreen):
    title = "Notas"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.notes_ui = NotesUI(self.content, controller_app=controller)
        self.notes_ui.grid(row=0, column=0, sticky="nsew")

    def on_show(self) -> None:
        super().on_show()
        self.notes_ui.on_show()
