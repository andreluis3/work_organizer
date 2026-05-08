from tkinter import messagebox

import customtkinter as ctk
from backend import task_manager
from backend.controllers.task_controller import TaskController
from frontend.components_tasks.cards_tasks import TaskCard, CourseCard, HistoryItem
from frontend.telas.base_screen import BaseScreen


FILTER_OPTIONS = {
    "Todos": "todos",
    "Pendente": "pendente",
    "Pausada": "pausada",
    "Concluida": "concluida",
}
SORT_OPTIONS = {
    "Prioridade": "prioridade",
    "Mais recentes": "recentes",
}


class TasksPage(BaseScreen):
    title = "Tasks"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content.grid_rowconfigure(2, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.task_controller = TaskController()
        self._current_filter = "Todos"
        self._current_sort = "Prioridade"

        # Cabeçalho
        self._create_header()
        # Filtros
        self._create_filters()
        # Container principal
        self._create_main_container()

        task_manager.clean_old_tasks()
        self.refresh()

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Tasks",
            font=("Segoe UI", 22, "bold"),
            text_color="#f8fbff",
        )
        self.header_title.grid(row=0, column=0, sticky="w")

        actions = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")

        self.new_task_btn = ctk.CTkButton(
            actions,
            text="+ New Task",
            hover_color="#1d4ed8",
            command=self._open_new_task,
        )
        self.new_task_btn.grid(row=0, column=0, padx=(0, 8))
        self.new_course_btn = ctk.CTkButton(actions, text="New Course", command=self._open_new_course)
        self.new_course_btn.grid(row=0, column=1)

    def _create_filters(self):
        self.filters_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.filters_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.filters_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            self.filters_frame,
            text="Status",
            font=("Segoe UI", 12, "bold"),
            text_color="#9cb0cf",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.filter = ctk.CTkOptionMenu(
            self.filters_frame,
            values=list(FILTER_OPTIONS.keys()),
            command=self._on_filter_change,
            width=140,
        )
        self.filter.set(self._current_filter)
        self.filter.grid(row=0, column=1, sticky="w", padx=(0, 18))

        ctk.CTkLabel(
            self.filters_frame,
            text="Ordenar",
            font=("Segoe UI", 12, "bold"),
            text_color="#9cb0cf",
        ).grid(row=0, column=2, sticky="w", padx=(0, 8))

        self.sort = ctk.CTkOptionMenu(
            self.filters_frame,
            values=list(SORT_OPTIONS.keys()),
            command=self._on_sort_change,
            width=150,
        )
        self.sort.set(self._current_sort)
        self.sort.grid(row=0, column=3, sticky="w")
            
    def _create_main_container(self):
        self.main_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.main_frame.grid(row=2, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.progress_section = _Section(self.main_frame, "Em andamento")
        self.progress_section.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        self.done_section = _Section(self.main_frame, "Concluidas")
        self.done_section.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        self.history_section = _Section(self.main_frame, "Historico")
        self.history_section.grid(row=2, column=0, sticky="ew")
        
    def _on_filter_change(self, value):
        self._current_filter = value
        self.refresh()

    def _on_sort_change(self, value):
        self._current_sort = value
        self.refresh()

    def _open_new_task(self):
        dialog = _TaskDialog(self, "Nova Task")
        self.wait_window(dialog)
        if dialog.result:
            title, subtasks, prioridade = dialog.result
            self.task_controller.create_task(title, subtasks, prioridade)
            self.refresh()

    def _open_new_course(self):
        dialog = _CourseDialog(self, "Novo Curso")
        self.wait_window(dialog)
        if dialog.result:
            title, total = dialog.result
            self.task_controller.create_course(title, total)
            self.refresh()

    def refresh(self):
        status_filter = FILTER_OPTIONS.get(self._current_filter, "todos")
        sort_by = SORT_OPTIONS.get(self._current_sort, "prioridade")
        visible = self.task_controller.list_tasks(status_filter=status_filter, sort_by=sort_by)
        history = self.task_controller.get_history_items()

        progress_items = [task for task in visible if task.get("status") != "concluida"]
        done_items = [task for task in visible if task.get("status") == "concluida"]

        callbacks = {
            "on_title_save": self._update_task_title,
            "on_completed_toggle": self._toggle_task_completed,
            "on_status_cycle": self._cycle_task_status,
            "on_subtask_toggle": self._toggle_subtask_completed,
            "on_progress_change": self.refresh,
        }
        self.progress_section.set_items(progress_items, callbacks)
        self.done_section.set_items(done_items, callbacks)
        self.history_section.set_history(history)

    def _update_task_title(self, task_id, title):
        try:
            return self.task_controller.update_title(task_id, title)
        except ValueError as exc:
            messagebox.showwarning("Task invalida", str(exc))
            return None

    def _toggle_task_completed(self, task_id, completed):
        updated = self.task_controller.toggle_completed(task_id, completed)
        self.after(80, self.refresh)
        return updated

    def _cycle_task_status(self, task_id):
        updated = self.task_controller.cycle_status(task_id)
        self.after(80, self.refresh)
        return updated

    def _toggle_subtask_completed(self, subtask_id, completed):
        updated = self.task_controller.set_subtask_completed(subtask_id, completed)
        self.after(80, self.refresh)
        return updated



class _Section(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=180)
        self.list_frame.grid(row=1, column=0, sticky="ew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text=title, font=("Segoe UI", 16, "bold"), text_color="#f8fbff")
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))

    def _clear(self):
        for child in self.list_frame.winfo_children():
            child.destroy()

    def set_items(self, items, callbacks=None):
        callbacks = callbacks or {}
        self._clear()
        if not items:
            ctk.CTkLabel(
                self.list_frame,
                text="Nothing here yet.",
                font=("Segoe UI", 12),
                text_color="#6f819f",
            ).grid(row=0, column=0, sticky="w", pady=6)
            return

        for row, task in enumerate(items):
            if task.get("type") == "course":
                card = CourseCard(
                    self.list_frame,
                    task=task,
                    course=task.get("course"),
                    on_progress_change=callbacks.get("on_progress_change"),
                )
            else:
                card = TaskCard(
                    self.list_frame,
                    task=task,
                    subtasks=task.get("subtasks", []),
                    on_title_save=callbacks.get("on_title_save"),
                    on_completed_toggle=callbacks.get("on_completed_toggle"),
                    on_status_cycle=callbacks.get("on_status_cycle"),
                    on_subtask_toggle=callbacks.get("on_subtask_toggle"),
                    on_progress_change=callbacks.get("on_progress_change"),
                )
            card.grid(row=row, column=0, sticky="ew", pady=6)

    def set_history(self, history):
        self._clear()
        if not history:
            ctk.CTkLabel(
                self.list_frame,
                text="No history yet.",
                font=("Segoe UI", 12),
                text_color="#6f819f",
            ).grid(row=0, column=0, sticky="w", pady=6)
            return

        for row, item in enumerate(history):
            card = HistoryItem(
                self.list_frame,
                title=item.get("title", ""),
                completed_at=item.get("completed_at", ""),
            )
            card.grid(row=row, column=0, sticky="ew", pady=6)

class _TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.result = None
        self.title(title)
        self.geometry("420x430")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())

        self.update_idletasks()

        self.after(
            50,
            lambda: (
                self.lift(),
                self.focus_force(),
                self.grab_set(),
            ),
        )

        ctk.CTkLabel(self, text="Title", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 6))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill="x", padx=20)
        self.title_entry.focus()

        ctk.CTkLabel(self, text="Prioridade", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 6)
        )
        self.priority_menu = ctk.CTkOptionMenu(self, values=["Alta", "Media", "Baixa"])
        self.priority_menu.set("Baixa")
        self.priority_menu.pack(fill="x", padx=20)

        ctk.CTkLabel(self, text="Subtasks (one per line)", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 6)
        )
        self.subtasks_box = ctk.CTkTextbox(self, height=140)
        self.subtasks_box.pack(fill="x", padx=20)

        action = ctk.CTkFrame(self, fg_color="transparent")
        action.pack(fill="x", padx=20, pady=20)
        action.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(action, text="Cancel", command=self._cancel).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(action, text="Create", command=self._confirm).grid(row=0, column=1, sticky="e")

    def _confirm(self):
        title = self.title_entry.get().strip()
        subtasks = self.subtasks_box.get("1.0", "end").splitlines()
        prioridade = {"Alta": 3, "Media": 2, "Baixa": 1}.get(self.priority_menu.get(), 1)
        if title:
            self.result = (title, subtasks, prioridade)
        self.destroy()

    def _cancel(self):
        self.destroy()


class _CourseDialog(ctk.CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.result = None
        self.title(title)
        self.geometry("380x260")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.focus_force()
        self.after(100, lambda: self.lift())

        ctk.CTkLabel(self, text="Course name", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(20, 6)
        )
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(self, text="Total lessons", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 6)
        )
        self.total_entry = ctk.CTkEntry(self)
        self.total_entry.insert(0, "10")
        self.total_entry.pack(fill="x", padx=20)

        action = ctk.CTkFrame(self, fg_color="transparent")
        action.pack(fill="x", padx=20, pady=20)
        action.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(action, text="Cancel", command=self._cancel).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(action, text="Create", command=self._confirm).grid(row=0, column=1, sticky="e")

    def _confirm(self):
        title = self.title_entry.get().strip()
        total_text = self.total_entry.get().strip()
        try:
            total = int(total_text)
        except ValueError:
            total = 1
        if title:
            self.result = (title, max(1, total))
        self.destroy()

    def _cancel(self):
        self.destroy()
