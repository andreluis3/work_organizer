from __future__ import annotations

import customtkinter as ctk

from backend.notes_manager import NotesManager



class NotesScreen(ctk.CTkFrame):
    title = "Notas"

    def __init__(self, master, controller):
        super().__init__(master, fg_color="#050c18")
        self.controller = controller
        self.notes_manager = NotesManager()
        self.current_note_id: int | None = None
        self.note_buttons: dict[int, ctk.CTkButton] = {}
        self.current_note_id: int | None = None
        self.current_note_name: str | None = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.title,
            font=("Segoe UI", 26, "bold"),
            text_color="#f8fbff",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=0)
        self.body.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_editor()

        self.load_notes()

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self.body, fg_color="#0f111a", corner_radius=14)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            textvariable=self.search_var,
            placeholder_text="Buscar notas...",
            height=36,
            fg_color="#111725",
            border_color="#1d2233",
            text_color="#f8fbff",
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        self.search_entry.bind("<KeyRelease>", self.search_notes)

        self.new_button = ctk.CTkButton(
            self.sidebar,
            text="+ Nova Nota",
            height=36,
            fg_color="#1a2234",
            hover_color="#1a1c29",
            text_color="#f8fbff",
            command=self.new_note,
        )
        self.new_button.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        self.notes_list = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="#0f111a",
            scrollbar_button_color="#1a1c29",
            scrollbar_button_hover_color="#2b2d3c",
        )
        self.notes_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.notes_list.grid_columnconfigure(0, weight=1)

    def _build_editor(self) -> None:
        self.editor = ctk.CTkFrame(self.body, fg_color="#050c18", corner_radius=14)
        self.editor.grid(row=0, column=1, sticky="nsew")
        self.editor.grid_rowconfigure(1, weight=1)
        self.editor.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(
            self.editor,
            placeholder_text="Título da nota",
            height=44,
            fg_color="#0f111a",
            border_color="#1d2233",
            text_color="#f8fbff",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        self.content_box = ctk.CTkTextbox(
            self.editor,
            fg_color="#0f111a",
            text_color="#f8fbff",
            border_color="#1d2233",
            border_width=1,
            corner_radius=10,
        )
        self.content_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))

        self.save_button = ctk.CTkButton(
            self.editor,
            text="Salvar",
            height=38,
            fg_color="#1a2234",
            hover_color="#1a1c29",
            text_color="#f8fbff",
            command=self.save_note,
        )

        self.delete_button = ctk.CTkButton(
            self.editor,
            text="Deletar",
            height=38,
            fg_color="#401a1a",
            hover_color="#5a1f1f",
            command=self.delete_note
        )
        self.delete_button.grid(row=2, column=0, sticky="w", padx=18)

        self.save_button.grid(row=2, column=0, sticky="e", padx=18, pady=(0, 18))

    def on_show(self) -> None:
        self.load_notes()
        if self.current_note_id is not None:
            self.open_note(self.current_note_id)

    def load_notes(self) -> None:
        notes = self.notes_manager.listar_notas()
        self.populate_notes_list(notes)

    def search_notes(self, _event=None) -> None:
        termo = self.search_var.get().strip()
        if termo:
            notes = self.notes_manager.buscar_notas(termo)
        else:
            notes = self.notes_manager.listar_notas()
        self.populate_notes_list(notes)

    def open_note(self, note_id: int) -> None:

        note = self.notes_manager.carregar_nota(note_id)

        if not note:
            self.current_note_id = None
            self.current_note_name = None
            self._clear_editor()
            return

        titulo, conteudo = note

        self.current_note_id = note_id
        self.current_note_name = titulo

    def new_note(self) -> None:
        note_id = self.notes_manager.criar_nota("Nova Nota", "")
        self.current_note_id = note_id
        self.search_var.set("")
        self.load_notes()
        self.open_note(note_id)

    def save_note(self) -> None:
        if self.current_note_id is None:
            return

        titulo = self.title_entry.get().strip() or "Nova Nota"
        conteudo = self.content_box.get("1.0", "end").strip()
        ok = self.notes_manager.atualizar_nota(
            self.current_note_id,
            titulo,
            conteudo
        )

        if not ok:
            print("Já existe uma nota com esse título.")
            return
        self.load_notes()
        self.open_note(self.current_note_id)

    def populate_notes_list(self, notes: list[tuple]) -> None:
        for child in self.notes_list.winfo_children():
            child.destroy()

        self.note_buttons = {}

        if not notes:
            empty_label = ctk.CTkLabel(
                self.notes_list,
                text="Nenhuma nota encontrada",
                text_color="#8a94b0",
                font=("Segoe UI", 12),
            )
            empty_label.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return

        for index, (note_id, titulo, _data) in enumerate(notes):
            label = titulo or "(Sem título)"
            button = ctk.CTkButton(
                self.notes_list,
                text=label,
                anchor="w",
                height=38,
                fg_color="#0f111a",
                hover_color="#1a1c29",
                text_color="#f8fbff",
                command=lambda nid=note_id: self.open_note(nid),
            )
            button.grid(row=index, column=0, sticky="ew", padx=6, pady=4)
            self.note_buttons[note_id] = button

        if self.current_note_id in self.note_buttons:
            self._highlight_note(self.current_note_id)

    def _highlight_note(self, note_id: int) -> None:
        for nid, button in self.note_buttons.items():
            if nid == note_id:
                button.configure(fg_color="#1a1c29")
            else:
                button.configure(fg_color="#0f111a")

    def _clear_editor(self) -> None:
        self.title_entry.delete(0, "end")
        self.content_box.delete("1.0", "end")

    def delete_note(self):

        if self.current_note_id is None:
            return

        note_name = self.current_note_name

        self.notes_manager.deletar_nota(self.current_note_id)

        print(f"Nota deletada: {note_name}")

        self.current_note_id = None
        self.current_note_name = None

        self._clear_editor()
        self.load_notes()