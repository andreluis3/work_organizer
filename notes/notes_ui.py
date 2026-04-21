from __future__ import annotations

import customtkinter as ctk

from notes.notes_controller import NotesController
from notes.templates import get_template_names


class NotesUI(ctk.CTkFrame):
    def __init__(self, master, controller_app=None, notes_controller: NotesController | None = None):
        super().__init__(master, fg_color="transparent")
        self.controller_app = controller_app
        self.notes_controller = notes_controller or NotesController()
        self.note_buttons: dict[int, ctk.CTkButton] = {}
        self._template_values = ["blank", *get_template_names()]

        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1, minsize=380)
        self.grid_columnconfigure(2, weight=1, minsize=360)
        self.grid_rowconfigure(0, weight=1)

        self._build_list_panel()
        self._build_editor_panel()
        self._build_preview_panel()

        self.notes_controller.bind(
            on_notes_change=self.render_notes_list,
            on_note_change=self.set_note_data,
            on_preview_change=self.set_preview_text,
            on_status_change=self.show_status,
        )
        self.notes_controller.initialize()

    def on_show(self) -> None:
        self.notes_controller.initialize()

    def _build_list_panel(self) -> None:
        self.list_panel = ctk.CTkFrame(
            self,
            fg_color="#0B1220",
            corner_radius=20,
            border_width=1,
            border_color="#1F2937",
        )
        self.list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.list_panel.grid_rowconfigure(3, weight=1)
        self.list_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.list_panel,
            text="Notas",
            font=("Segoe UI", 22, "bold"),
            text_color="#F8FBFF",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.list_panel,
            textvariable=self.search_var,
            placeholder_text="Buscar notas...",
            fg_color="#111827",
            border_color="#263449",
            text_color="#F8FBFF",
            height=38,
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        actions = ctk.CTkFrame(self.list_panel, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self.new_button = ctk.CTkButton(
            actions,
            text="+ Nova",
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            text_color="#04111F",
            command=lambda: self.notes_controller.create_note(),
        )
        self.new_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.template_menu = ctk.CTkOptionMenu(
            actions,
            values=self._template_values,
            fg_color="#111827",
            button_color="#1F2937",
            button_hover_color="#334155",
            dropdown_fg_color="#111827",
            dropdown_hover_color="#1F2937",
            text_color="#F8FBFF",
            command=self._create_from_template,
        )
        self.template_menu.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.template_menu.set("blank")

        self.notes_list = ctk.CTkScrollableFrame(
            self.list_panel,
            fg_color="transparent",
            scrollbar_button_color="#1F2937",
            scrollbar_button_hover_color="#334155",
        )
        self.notes_list.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.notes_list.grid_columnconfigure(0, weight=1)

    def _build_editor_panel(self) -> None:
        self.editor_panel = ctk.CTkFrame(
            self,
            fg_color="#0B1220",
            corner_radius=20,
            border_width=1,
            border_color="#1F2937",
        )
        self.editor_panel.grid(row=0, column=1, sticky="nsew", padx=10)
        self.editor_panel.grid_rowconfigure(2, weight=1)
        self.editor_panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.editor_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            header,
            text="Editor",
            font=("Segoe UI", 22, "bold"),
            text_color="#F8FBFF",
        ).grid(row=0, column=0, sticky="w")

        self.save_button = ctk.CTkButton(
            header,
            text="Salvar",
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#03130B",
            command=self._save_note,
            width=96,
        )
        self.save_button.grid(row=0, column=1, padx=(8, 8))

        self.delete_button = ctk.CTkButton(
            header,
            text="Excluir",
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color="#FEE2E2",
            command=self.notes_controller.delete_current_note,
            width=96,
        )
        self.delete_button.grid(row=0, column=2)

        self.title_entry = ctk.CTkEntry(
            self.editor_panel,
            placeholder_text="Titulo da nota",
            fg_color="#111827",
            border_color="#263449",
            text_color="#F8FBFF",
            font=("Segoe UI", 18, "bold"),
            height=42,
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        self.editor_box = ctk.CTkTextbox(
            self.editor_panel,
            fg_color="#0D1117",
            text_color="#E6EDF3",
            border_color="#263449",
            border_width=1,
            corner_radius=14,
            font=("JetBrains Mono", 14),
            wrap="word",
        )
        self.editor_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.editor_box.bind("<KeyRelease>", self._on_editor_change)

        self.status_label = ctk.CTkLabel(
            self.editor_panel,
            text="Pronto.",
            font=("Segoe UI", 12),
            text_color="#94A3B8",
        )
        self.status_label.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 16))

    def _build_preview_panel(self) -> None:
        self.preview_panel = ctk.CTkFrame(
            self,
            fg_color="#0B1220",
            corner_radius=20,
            border_width=1,
            border_color="#1F2937",
        )
        self.preview_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        self.preview_panel.grid_rowconfigure(1, weight=1)
        self.preview_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.preview_panel,
            text="Preview",
            font=("Segoe UI", 22, "bold"),
            text_color="#F8FBFF",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))

        self.preview_box = ctk.CTkTextbox(
            self.preview_panel,
            fg_color="#0D1117",
            text_color="#C9D1D9",
            border_color="#263449",
            border_width=1,
            corner_radius=14,
            font=("Consolas", 13),
            wrap="word",
        )
        self.preview_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.preview_box.configure(state="disabled")

    def render_notes_list(self, notes: list[tuple]) -> None:
        for child in self.notes_list.winfo_children():
            child.destroy()

        self.note_buttons = {}
        if not notes:
            ctk.CTkLabel(
                self.notes_list,
                text="Nenhuma nota encontrada.",
                text_color="#94A3B8",
                font=("Segoe UI", 12),
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=12)
            return

        for row, (note_id, title, updated_at) in enumerate(notes):
            card = ctk.CTkButton(
                self.notes_list,
                text=self._format_note_label(title or "Sem titulo", updated_at),
                anchor="w",  # alinhamento correto
                height=54,
                fg_color="#111827",
                hover_color="#172036",
                text_color="#F8FBFF",
                command=lambda nid=note_id: self.notes_controller.load_note(nid),
            )

            card.grid(row=row, column=0, sticky="ew", padx=4, pady=4)
            self.note_buttons[note_id] = card

    def set_note_data(self, note_data: dict) -> None:
        note_id = note_data.get("id")
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note_data.get("title", ""))

        self.editor_box.delete("1.0", "end")
        self.editor_box.insert("1.0", note_data.get("content", ""))
        self._highlight_selected_note(note_id)

    def set_preview_text(self, content: str) -> None:
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", content)
        self.preview_box.configure(state="disabled")

    def show_status(self, level: str, message: str) -> None:
        colors = {
            "success": "#22C55E",
            "warning": "#F59E0B",
            "info": "#94A3B8",
        }
        self.status_label.configure(text=message, text_color=colors.get(level, "#94A3B8"))
        if self.controller_app and hasattr(self.controller_app, "toast"):
            self.controller_app.toast(message, level="info" if level == "warning" else level)

    def _highlight_selected_note(self, note_id: int | None) -> None:
        for current_id, button in self.note_buttons.items():
            button.configure(fg_color="#172036" if current_id == note_id else "#111827")

    def _format_note_label(self, title: str, updated_at) -> str:
        when = str(updated_at or "").replace("T", " ")
        preview_date = when[:16] if when else "Sem data"
        return f"{title}\n{preview_date}"

    def _on_search_change(self, _event=None) -> None:
        self.notes_controller.refresh_notes(self.search_var.get())

    def _on_editor_change(self, _event=None) -> None:
        self.notes_controller.update_preview(self.editor_box.get("1.0", "end-1c"))

    def _create_from_template(self, template_name: str) -> None:
        if template_name == "blank":
            return
        self.notes_controller.create_note(template_name=template_name)
        self.template_menu.set("blank")

    def _save_note(self) -> None:
        self.notes_controller.save_note(
            self.title_entry.get(),
            self.editor_box.get("1.0", "end-1c"),
        )
