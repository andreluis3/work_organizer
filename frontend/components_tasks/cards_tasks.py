import customtkinter as ctk

from backend import task_manager


class TaskCard(ctk.CTkFrame):
    def __init__(self, master, task, subtasks, on_progress_change=None, **kwargs):
        super().__init__(
            master,
            fg_color="#111827"  ,
            border_color="#263449",
            border_width=1,
            corner_radius=16,
            **kwargs,
        )

        self.task = task
        self.subtasks = subtasks
        self.on_progress_change = on_progress_change
        self._vars = []

        title = ctk.CTkLabel(
            self,
            text=task.get("title", "Task"),
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
        )
        title.pack(anchor="w", padx=16, pady=(14, 8))

        self.checks_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.checks_frame.pack(fill="x", padx=16)

        for subtask in subtasks:
            var = ctk.IntVar(value=int(subtask.get("completed", 0)))
            self._vars.append(var)
            checkbox = ctk.CTkCheckBox(
                self.checks_frame,
                text=subtask.get("description", ""),
                variable=var,
                onvalue=1,
                offvalue=0,
                command=lambda s=subtask, v=var: self._on_toggle(s, v),
            )
            checkbox.pack(anchor="w", pady=4)
            if var.get() == 1:
                checkbox.configure(state="disabled")

        self.progress = ctk.CTkProgressBar(self, height=10)
        self.progress.pack(fill="x", padx=16, pady=(10, 16))
        self._update_progress()
        
        self.bind("<Enter>", lambda e: self.configure(fg_color="#1f2937"))
        self.bind("<Leave>", lambda e: self.configure(fg_color="#111827"))

    def _on_toggle(self, subtask, var):
        if var.get() != 1:
            return
        task_manager.complete_subtask(subtask["id"])
        self._disable_checkbox(subtask["id"])
        self._update_progress()
        if self.on_progress_change:
            self.on_progress_change()

    def _disable_checkbox(self, subtask_id):
        for child, subtask in zip(self.checks_frame.winfo_children(), self.subtasks):
            if isinstance(child, ctk.CTkCheckBox) and subtask.get("id") == subtask_id:
                child.configure(state="disabled")

    def _update_progress(self):
        total = len(self._vars)
        completed = sum(var.get() for var in self._vars)
        progress = completed / total if total else 0
        self.progress.set(progress)


class CourseCard(ctk.CTkFrame):
    def __init__(self, master, task, course, on_progress_change=None, **kwargs):
        super().__init__(
            master,
            fg_color="#111827"  ,
            border_color="#263449",
            border_width=1,
            corner_radius=16,
            **kwargs,
        )

        self.task = task
        self.course = course or {}
        self.on_progress_change = on_progress_change

        title = ctk.CTkLabel(
            self,
            text=task.get("title", "Curso"),
            font=("Segoe UI", 16, "bold"),
            text_color="#f8fbff",
        )
        title.pack(anchor="w", padx=16, pady=(14, 4))

        self.progress_label = ctk.CTkLabel(
            self,
            text="Progresso: 0/0",
            font=("Segoe UI", 12),
            text_color="#9cb0cf",
        )
        self.progress_label.pack(anchor="w", padx=16, pady=(0, 6))

        self.progress = ctk.CTkProgressBar(self, height=10)
        self.progress.pack(fill="x", padx=16)

        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.pack(fill="x", padx=16, pady=(8, 8))

        self.slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=max(1, int(self.course.get("total_lessons", 1))),
            command=self._on_slider,
        )
        self.slider.pack(fill="x")

        lesson_frame = ctk.CTkFrame(self, fg_color="transparent")
        lesson_frame.pack(fill="x", padx=16, pady=(0, 14))
        lesson_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            lesson_frame,
            text="Aula atual",
            font=("Segoe UI", 12),
            text_color="#9cb0cf",
        ).grid(row=0, column=0, sticky="w")

        self.lesson_entry = ctk.CTkEntry(lesson_frame)
        self.lesson_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.lesson_entry.insert(0, self.course.get("current_lesson", "Aula 1"))
        self.lesson_entry.bind("<Return>", self._on_lesson_change)
        self.lesson_entry.bind("<FocusOut>", self._on_lesson_change)

        self._load_initial_progress()

    def _load_initial_progress(self):
        total = max(1, int(self.course.get("total_lessons", 1)))
        progress = int(self.course.get("progress", 0))
        completed = int((progress / 100) * total)
        self.slider.configure(to=total)
        self.slider.set(completed)
        self._apply_progress(completed)

    def _on_slider(self, value):
        completed = int(round(value))
        self._apply_progress(completed)
        self._persist_progress(completed)

    def _on_lesson_change(self, _event):
        completed = int(round(self.slider.get()))
        self._persist_progress(completed)

    def _apply_progress(self, completed):
        total = max(1, int(self.course.get("total_lessons", 1)))
        progress = completed / total
        self.progress.set(progress)
        self.progress_label.configure(text=f"Progresso: {completed}/{total}")

    def _persist_progress(self, completed):
        total = max(1, int(self.course.get("total_lessons", 1)))
        current_lesson = self.lesson_entry.get().strip() or "Aula 1"
        progress = task_manager.update_course_progress(
            self.task["id"],
            completed,
            current_lesson,
            total,
        )
        self.course["progress"] = progress
        self.course["current_lesson"] = current_lesson
        if self.on_progress_change:
            self.on_progress_change()


class HistoryItem(ctk.CTkFrame):
    def __init__(self, master, title, completed_at, **kwargs):
        super().__init__(
            master,
            fg_color="#111827"  ,
            hover_color="#1f2937",
            border_color="#263449",
            border_width=1,
            corner_radius=12,
            **kwargs,
        )

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color="#f8fbff",
        )
        title_label.pack(anchor="w", padx=12, pady=(10, 2))

        date_label = ctk.CTkLabel(
            self,
            text=completed_at,
            font=("Segoe UI", 11),
            text_color="#9cb0cf",
        )
        date_label.pack(anchor="w", padx=12, pady=(0, 10))
