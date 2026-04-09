import customtkinter as ctk
from backend import task_manager
from frontend.components_tasks.cards_tasks import TaskCard, CourseCard, HistoryItem
from frontend.telas.base_screen import BaseScreen


class TasksPage(BaseScreen):
    title = "Tasks"

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.content.grid_rowconfigure(2, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current_filter = "Todas"

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

        self.new_task_btn = ctk.CTkButton(actions, text="New Task", command=self._open_new_task)
        self.new_task_btn.grid(row=0, column=0, padx=(0, 8))
        self.new_course_btn = ctk.CTkButton(actions, text="New Course", command=self._open_new_course)
        self.new_course_btn.grid(row=0, column=1)

    def _create_filters(self):
        self.filters_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.filters_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.filter = ctk.CTkSegmentedButton(
            self.filters_frame,
            values=["Todas", "Em Progresso", "Feitas", "Estagnadas"],
            command=self._on_filter_change,
        )
        self.filter.set("Todas")
        self.filter.pack(anchor="w")

    def _create_main_container(self):
        self.main_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.main_frame.grid(row=2, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.tasks_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tasks_container.grid(row=0, column=0, sticky="nsew")
        self.tasks_container.grid_columnconfigure(0, weight=1)

        # Seções (visíveis de acordo com o filtro)
        self.progress_section = _Section(self.tasks_container, "Tasks em Progresso")
        self.done_section = _Section(self.tasks_container, "Tasks Concluídas")
        self.stagnant_section = _Section(self.tasks_container, "Tasks Estagnadas")
        self.history_section = _Section(self.tasks_container, "Histórico")

    def _on_filter_change(self, value):
        self._current_filter = value
        self.refresh()

    def refresh(self):
        tasks = task_manager.get_all_tasks()
        stagnant = task_manager.get_stagnant_tasks()
        history = task_manager.get_history_items()

        # Filtragem dinâmica
        if self._current_filter == "Em Progresso":
            visible = [t for t in tasks if t.get("status") != "done"]
        elif self._current_filter == "Feitas":
            visible = [t for t in tasks if t.get("status") == "done"]
        elif self._current_filter == "Estagnadas":
            visible = stagnant
        else:
            visible = tasks

        # Separação por seção
        progress_items = [t for t in visible if t.get("status") != "done"]
        done_items = [t for t in visible if t.get("status") == "done"]

        # Limpar e mostrar seções conforme necessário
        self.progress_section.set_items(progress_items)
        self.done_section.set_items(done_items)
        self.stagnant_section.set_items(visible if self._current_filter == "Estagnadas" else [])
        self.history_section.set_history(history)

    def _open_new_task(self):
        dialog = _TaskDialog(self, "Nova Task")
        self.wait_window(dialog)
        if dialog.result:
            title, subtasks = dialog.result
            task_manager.create_task(title, subtasks)
            self.refresh()

    def _open_new_course(self):
        dialog = _CourseDialog(self, "Novo Curso")
        self.wait_window(dialog)
        if dialog.result:
            title, total = dialog.result
            task_manager.create_course(title, total)
            self.refresh()

    def refresh(self):
        tasks = task_manager.get_all_tasks()
        stagnant = task_manager.get_stagnant_tasks()
        history = task_manager.get_history_items()

        if self._current_filter == "Em Progresso":
            visible = [task for task in tasks if task.get("status") != "done"]
        elif self._current_filter == "Feitas":
            visible = [task for task in tasks if task.get("status") == "done"]
        elif self._current_filter == "Estagnadas":
            visible = stagnant
        else:
            visible = tasks

        progress_items = [task for task in visible if task.get("status") != "done"]
        done_items = [task for task in visible if task.get("status") == "done"]

        self.progress_section.set_items(progress_items)
        self.done_section.set_items(done_items)
        self.history_section.set_history(history)



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

    def set_items(self, items):
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
                card = CourseCard(self.list_frame, task=task, course=task.get("course"))
            else:
                card = TaskCard(self.list_frame, task=task, subtasks=task.get("subtasks", []))
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
        self.geometry("420x360")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Title", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 6))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill="x", padx=20)

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
        if title:
            self.result = (title, subtasks)
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
        self.grab_set()

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
