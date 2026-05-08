from __future__ import annotations

import customtkinter as ctk

from notes.notes_controller import NotesController


def apply_markdown_formatting(textbox):
    tag_styles = {
        "md_h1": {
            "foreground": "#22C55E",
             "spacing1": 12,
            "spacing3": 12,
            "lmargin1": 6,
            },
        "md_h2": {
            "foreground": "#38BDF8",
            "spacing1": 6,
            "spacing3": 6,
        },
        "md_checkbox": {
            "foreground": "#94A3B8",
        },
        "md_code": {
            "foreground": "#E5E7EB",
            "background": "#111827",
            "spacing1": 4,
            "spacing3": 4,
        },
    }

    for tag_name, style in tag_styles.items():
        textbox.tag_config(tag_name, **style)
        textbox.tag_remove(tag_name, "1.0", "end")

    end_line = int(textbox.index("end-1c").split(".")[0])
    in_code_block = False

    for line_number in range(1, end_line + 1):
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        line = textbox.get(line_start, line_end)
        stripped = line.strip()

        if stripped.startswith("```"):
            textbox.tag_add("md_code", line_start, line_end)
            in_code_block = not in_code_block
            continue

        if in_code_block:
            textbox.tag_add("md_code", line_start, line_end)
            continue

        if line.startswith("# "):
            textbox.tag_add("md_h1", line_start, line_end)
            continue

        if line.startswith("## "):
            textbox.tag_add("md_h2", line_start, line_end)
            continue

        marker_index = line.find("- [ ]")
        if marker_index >= 0 and not line[:marker_index].strip():
            marker_start = f"{line_number}.{marker_index}"
            marker_end = f"{line_number}.{marker_index + 5}"
            textbox.tag_add("md_checkbox", marker_start, marker_end)

def enhance_block_visual(textbox):
    block_tags = {
        "block_even": {
            "background": "#0D1117",
            "spacing1": 4,
            "spacing3": 8,
            "lmargin1": 10,
            "lmargin2": 10,
            "rmargin": 10,
        },
        "block_odd": {
            "background": "#101621",
            "spacing1": 4,
            "spacing3": 8,
            "lmargin1": 10,
            "lmargin2": 10,
            "rmargin": 10,
        },
        "current_line": {
            "background": "#172033",
            "spacing1": 4,
            "spacing3": 8,
            "lmargin1": 12,
            "lmargin2": 12,
            "rmargin": 10,
        },
    }

    for tag_name, style in block_tags.items():
        textbox.tag_config(tag_name, **style)
        textbox.tag_remove(tag_name, "1.0", "end")

    end_line = int(textbox.index("end-1c").split(".")[0])
    paragraph_index = 0
    paragraph_start = None

    for line_number in range(1, end_line + 2):
        line = textbox.get(f"{line_number}.0", f"{line_number}.end") if line_number <= end_line else ""
        is_blank = not line.strip()

        if paragraph_start is None and not is_blank:
            paragraph_start = line_number

        if paragraph_start is not None and (is_blank or line_number == end_line + 1):
            paragraph_end = line_number - 1
            tag_name = "block_even" if paragraph_index % 2 == 0 else "block_odd"
            textbox.tag_add(tag_name, f"{paragraph_start}.0", f"{paragraph_end}.end")
            paragraph_index += 1
            paragraph_start = None

    current_line = textbox.index("insert").split(".")[0]
    textbox.tag_add("current_line", f"{current_line}.0", f"{current_line}.end")
    textbox.tag_raise("current_line")


class SlashCommandMenu:
    COMMANDS = [
        {"label": "/todo", "description": "Checklist item", "insert": "- [ ] "},
        {"label": "/code", "description": "Code block", "insert": "```\n\n```"},
        {"label": "/h1", "description": "Heading 1", "insert": "# "},
        {"label": "/h2", "description": "Heading 2", "insert": "## "},
    ]

    def __init__(self, textbox: ctk.CTkTextbox):
        self.textbox = textbox
        self.master = textbox.master
        self.frame: ctk.CTkFrame | None = None
        self.buttons: list[ctk.CTkButton] = []
        self.filtered_commands = self.COMMANDS[:]
        self.selected_index = 0
        self.slash_index: str | None = None
        self.is_open = False

        self.textbox.bind("<KeyRelease>", self._on_key_release, add="+")
        self.textbox.bind("<Up>", self._on_arrow_up, add="+")
        self.textbox.bind("<Down>", self._on_arrow_down, add="+")
        self.textbox.bind("<Return>", self._on_enter, add="+")
        self.textbox.bind("<Escape>", self._on_escape, add="+")
        self.textbox.bind("<Button-1>", self._on_click_outside, add="+")

    def _on_key_release(self, event=None):
        if event and event.keysym == "slash":
            self.slash_index = self.textbox.index("insert-1c")
            self.open()
            return

        if not self.is_open:
            return

        query = self._current_query()
        if query is None:
            self.close()
            return

        self.filtered_commands = [
            command for command in self.COMMANDS if command["label"].startswith(query)
        ]
        self.selected_index = 0

        if not self.filtered_commands:
            self.close()
            return

        self._render()
        self._position_near_cursor()

    def open(self):
        if self.frame is None:
            self.frame = ctk.CTkFrame(
                self.master,
                fg_color="#111827",
                border_color="#263449",
                border_width=1,
                corner_radius=8,
            )

        self.filtered_commands = self.COMMANDS[:]
        self.selected_index = 0
        self.is_open = True
        self._render()
        self._position_near_cursor()
        self.frame.lift()

    def close(self):
        if self.frame is not None:
            self.frame.place_forget()
        self.is_open = False
        self.slash_index = None
        self.selected_index = 0

    def _render(self):
        if self.frame is None:
            return

        for child in self.frame.winfo_children():
            child.destroy()
        self.buttons = []

        for index, command in enumerate(self.filtered_commands):
            selected = index == self.selected_index
            button = ctk.CTkButton(
                self.frame,
                text=f"{command['label']}  {command['description']}",
                anchor="w",
                height=34,
                width=210,
                fg_color="#1F2937" if selected else "#111827",
                hover_color="#263449",
                text_color="#F8FBFF",
                command=lambda item=command: self._insert_command(item),
            )
            button.grid(row=index, column=0, sticky="ew", padx=6, pady=(6 if index == 0 else 2, 6 if index == len(self.filtered_commands) - 1 else 2))
            self.buttons.append(button)

    def _position_near_cursor(self):
        if self.frame is None:
            return

        bbox = self._cursor_bbox()
        x = self.textbox.winfo_x() + 18
        y = self.textbox.winfo_y() + 28

        if bbox:
            cursor_x, cursor_y, _width, height = bbox
            x = self.textbox.winfo_x() + cursor_x + 18
            y = self.textbox.winfo_y() + cursor_y + height + 18

        self.frame.place(x=x, y=y)

    def _cursor_bbox(self):
        try:
            return self.textbox.bbox("insert")
        except Exception:
            pass

        inner_textbox = getattr(self.textbox, "_textbox", None)
        if inner_textbox is None:
            return None

        try:
            return inner_textbox.bbox("insert")
        except Exception:
            return None

    def _current_query(self):
        if not self.slash_index:
            return None

        try:
            value = self.textbox.get(self.slash_index, "insert")
        except Exception:
            return None

        if not value.startswith("/") or "\n" in value or "\t" in value or " " in value:
            return None
        return value

    def _move_selection(self, step: int):
        if not self.is_open or not self.filtered_commands:
            return

        self.selected_index = (self.selected_index + step) % len(self.filtered_commands)
        self._render()

    def _insert_selected(self):
        if not self.is_open or not self.filtered_commands:
            return
        self._insert_command(self.filtered_commands[self.selected_index])

    def _insert_command(self, command):
        if self.slash_index:
            self.textbox.delete(self.slash_index, "insert")
        self.textbox.insert("insert", command["insert"])
        self.close()
        self.textbox.focus_set()
        self.textbox.event_generate("<KeyRelease>")

    def _on_arrow_up(self, _event=None):
        if not self.is_open:
            return None
        self._move_selection(-1)
        return "break"

    def _on_arrow_down(self, _event=None):
        if not self.is_open:
            return None
        self._move_selection(1)
        return "break"

    def _on_enter(self, _event=None):
        if not self.is_open:
            return None
        self._insert_selected()
        return "break"

    def _on_escape(self, _event=None):
        if not self.is_open:
            return None
        self.close()
        return "break"

    def _on_click_outside(self, _event=None):
        if self.is_open:
            self.close()


class NotesUI(ctk.CTkFrame):
    def __init__(self, master, controller_app=None, notes_controller: NotesController | None = None):
        super().__init__(master, fg_color="transparent")
        self.controller_app = controller_app
        self.notes_controller = notes_controller or NotesController()
        self.note_buttons: dict[int, ctk.CTkButton] = {}

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
            on_tags_change=self.update_tags,
            on_insight_change=self.update_insight,
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

        self.new_button = ctk.CTkButton(
            actions,
            text="+ Nova",
            fg_color="#0EA5E9",
            hover_color="#0284C7",
            text_color="#04111F",
            command=self.notes_controller.create_note,
        )
        self.new_button.grid(row=0, column=0, sticky="ew")

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
        self.editor_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.editor_box.bind("<KeyRelease>", self._on_editor_change)
        self.editor_box.bind("<ButtonRelease-1>", self._on_editor_cursor_move)
        self.slash_commands = SlashCommandMenu(self.editor_box)

        self.tags_label = ctk.CTkLabel(
            self.editor_panel,
            text="Tags:",
            font=("Segoe UI", 12, "bold"),
            text_color="#22C55E",
            anchor="w",
        )
        self.tags_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 4))

        self.insight_label = ctk.CTkLabel(
            self.editor_panel,
            text="",
            font=("Segoe UI", 12),
            text_color="#38BDF8",
            anchor="w",
            wraplength=460,
        )
        self.insight_label.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 8))

        self.status_label = ctk.CTkLabel(
            self.editor_panel,
            text="Pronto.",
            font=("Segoe UI", 12),
            text_color="#94A3B8",
            anchor="w",
        )
        self.status_label.grid(row=5, column=0, sticky="w", padx=18, pady=(0, 16))

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
                anchor="w",
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
        apply_markdown_formatting(self.editor_box)
        enhance_block_visual(self.editor_box)
        self._highlight_selected_note(note_id)

    def set_preview_text(self, content: str) -> None:
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", content)
        self.preview_box.configure(state="disabled")

    def update_tags(self, tags) -> None:
        text = ", ".join(str(tag) for tag in tags) if tags else ""
        self.tags_label.configure(text=f"Tags: {text}" if text else "Tags:")

    def update_insight(self, insight) -> None:
        self.insight_label.configure(text=str(insight or ""))

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
        apply_markdown_formatting(self.editor_box)
        enhance_block_visual(self.editor_box)
        self.notes_controller.process_text(self.editor_box.get("1.0", "end-1c"))

    def _on_editor_cursor_move(self, _event=None) -> None:
        enhance_block_visual(self.editor_box)

    def _save_note(self) -> None:
        self.notes_controller.save_note(
            self.title_entry.get(),
            self.editor_box.get("1.0", "end-1c"),
        )
