import customtkinter as ctk

from backend import task_manager
from frontend.components_tasks.cards_tasks import TaskCard, CourseCard, HistoryItem
from frontend.telas.base_screen import BaseScreen


class TasksPage(BaseScreen):
    title = "Tasks"

    def __init__(self, master, controller):
        super().__init__(master, controller)

        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current_filter = "Todas"

        self.top_bar = ctk.CTkFrame(self.content, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.top_bar.grid_columnconfigure(3, weight=1)

        self.new_task_btn = ctk.CTkButton(
            self.top_bar,
            text="Nova Task",
            command=self._open_new_task,
        )
        self.new_task_btn.grid(row=0, column=0, padx=(0, 8))

        self.new_course_btn = ctk.CTkButton(
            self.top_bar,
            text="Novo Curso",
            command=self._open_new_course,
        )
        self.new_course_btn.grid(row=0, column=1, padx=(0, 12))

        self.filter = ctk.CTkSegmentedButton(
            self.top_bar,
            values=["Todas", "Pendentes", "Cursos", "Estagnadas"],
            command=self._on_filter_change,
        )
        self.filter.set("Todas")
        self.filter.grid(row=0, column=2, sticky="w")

        self.main_area = ctk.CTkFrame(self.content, fg_color="transparent")
        self.main_area.grid(row=1, column=0, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=3)
        self.main_area.grid_columnconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        self.cards_frame = ctk.CTkScrollableFrame(
            self.main_area,
            fg_color="transparent",
            width=620,
            height=360,
        )
        self.cards_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        self.analytics = ctk.CTkFrame(
            self.main_area,
            fg_color="#0b1220",
            border_color="#263449",
            border_width=1,
            corner_radius=16,
        )
        self.analytics.grid(row=0, column=1, sticky="nsew")
        self.analytics.grid_columnconfigure(0, weight=1)

        self.analytics_title = ctk.CTkLabel(
            self.analytics,
            text="Analytics",
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
        )
        self.analytics_title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))

        self.analytics_values = {
            "total": ctk.CTkLabel(self.analytics, text="--", font=("Segoe UI", 13), text_color="#9cb0cf"),
            "pending": ctk.CTkLabel(self.analytics, text="--", font=("Segoe UI", 13), text_color="#9cb0cf"),
            "courses": ctk.CTkLabel(self.analytics, text="--", font=("Segoe UI", 13), text_color="#9cb0cf"),
            "stagnant": ctk.CTkLabel(self.analytics, text="--", font=("Segoe UI", 13), text_color="#9cb0cf"),
        }

        labels = {
            "total": "Total de itens",
            "pending": "Pendentes",
            "courses": "Cursos",
            "stagnant": "Estagnadas",
        }
        row = 1
        for key, label in labels.items():
            ctk.CTkLabel(
                self.analytics,
                text=label,
                font=("Segoe UI", 12),
                text_color="#6f819f",
            ).grid(row=row, column=0, sticky="w", padx=16)
            self.analytics_values[key].grid(row=row + 1, column=0, sticky="w", padx=16, pady=(0, 10))
            row += 2

        self.history_area = ctk.CTkFrame(self.content, fg_color="transparent")
        self.history_area.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        self.history_area.grid_columnconfigure(0, weight=1)

        self.history_title = ctk.CTkLabel(
            self.history_area,
            text="Histórico",
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
        )
        self.history_title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.history_frame = ctk.CTkScrollableFrame(
            self.history_area,
            fg_color="transparent",
            height=140,
        )
        self.history_frame.grid(row=1, column=0, sticky="ew")

        task_manager.clean_old_tasks()
        self.refresh()

    def _on_filter_change(self, value):
        self._current_filter = value
        self.refresh()

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
        for child in self.cards_frame.winfo_children():
            child.destroy()
        for child in self.history_frame.winfo_children():
            child.destroy()

        tasks = task_manager.get_all_tasks()
        stagnant = task_manager.get_stagnant_tasks()
        history = task_manager.get_history_items()

        if self._current_filter == "Pendentes":
            filtered = [task for task in tasks if task.get("type") == "task" and task.get("status") != "done"]
        elif self._current_filter == "Cursos":
            filtered = [task for task in tasks if task.get("type") == "course"]
        elif self._current_filter == "Estagnadas":
            filtered = stagnant
        else:
            filtered = tasks

        if not filtered:
            ctk.CTkLabel(
                self.cards_frame,
                text="Nada por aqui ainda.",
                font=("Segoe UI", 14),
                text_color="#6f819f",
            ).pack(anchor="center", pady=24)
        else:
            for task in filtered:
                if task.get("type") == "course":
                    card = CourseCard(
                        self.cards_frame,
                        task=task,
                        course=task.get("course"),
                        on_progress_change=self._update_analytics,
                    )
                else:
                    card = TaskCard(
                        self.cards_frame,
                        task=task,
                        subtasks=task.get("subtasks", []),
                        on_progress_change=self._update_analytics,
                    )
                card.pack(fill="x", pady=8)

        if not history:
            ctk.CTkLabel(
                self.history_frame,
                text="Sem histórico ainda.",
                font=("Segoe UI", 12),
                text_color="#6f819f",
            ).pack(anchor="w", pady=6)
        else:
            for item in history:
                card = HistoryItem(
                    self.history_frame,
                    title=item.get("title", ""),
                    completed_at=item.get("completed_at", ""),
                )
                card.pack(fill="x", pady=6)

        self._update_analytics(tasks, stagnant)

    def _update_analytics(self, tasks=None, stagnant=None):
        tasks = tasks if tasks is not None else task_manager.get_all_tasks()
        stagnant = stagnant if stagnant is not None else task_manager.get_stagnant_tasks()

        total = len(tasks)
        pending = len([task for task in tasks if task.get("status") != "done" and task.get("type") == "task"])
        courses = len([task for task in tasks if task.get("type") == "course"])
        stagnant_count = len(stagnant)

        self.analytics_values["total"].configure(text=str(total))
        self.analytics_values["pending"].configure(text=str(pending))
        self.analytics_values["courses"].configure(text=str(courses))
        self.analytics_values["stagnant"].configure(text=str(stagnant_count))


class _TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.result = None
        self.title(title)
        self.geometry("420x360")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Título", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 6))
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(self, text="Subtasks (uma por linha)", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 6)
        )
        self.subtasks_box = ctk.CTkTextbox(self, height=140)
        self.subtasks_box.pack(fill="x", padx=20)

        action = ctk.CTkFrame(self, fg_color="transparent")
        action.pack(fill="x", padx=20, pady=20)
        action.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(action, text="Cancelar", command=self._cancel).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(action, text="Criar", command=self._confirm).grid(row=0, column=1, sticky="e")

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

        ctk.CTkLabel(self, text="Nome do curso", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(20, 6)
        )
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(self, text="Total de aulas", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", padx=20, pady=(16, 6)
        )
        self.total_entry = ctk.CTkEntry(self)
        self.total_entry.insert(0, "10")
        self.total_entry.pack(fill="x", padx=20)

        action = ctk.CTkFrame(self, fg_color="transparent")
        action.pack(fill="x", padx=20, pady=20)
        action.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(action, text="Cancelar", command=self._cancel).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(action, text="Criar", command=self._confirm).grid(row=0, column=1, sticky="e")

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
