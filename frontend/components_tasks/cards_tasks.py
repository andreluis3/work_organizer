import customtkinter as ctk

from backend import task_manager


STATUS_LABELS = {
    "pendente": "Pendente",
    "pausada": "Pausada",
    "concluida": "Concluida",
}
PRIORITY_LABELS = {
    3: ("Alta", "#ef4444"),
    2: ("Media", "#eab308"),
    1: ("Baixa", "#64748b"),
}


class TaskCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        task,
        subtasks,
        on_title_save=None,
        on_completed_toggle=None,
        on_status_cycle=None,
        on_subtask_toggle=None,
        on_progress_change=None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color="#111827"  ,
            border_color="#263449",
            border_width=1,
            corner_radius=8,
            **kwargs,
        )

        self.task = task
        self.subtasks = subtasks
        self.on_title_save = on_title_save
        self.on_completed_toggle = on_completed_toggle
        self.on_status_cycle = on_status_cycle
        self.on_subtask_toggle = on_subtask_toggle
        self.on_progress_change = on_progress_change
        self._vars = []
        self._editing = False

        self.grid_columnconfigure(1, weight=1)

        self.completed_var = ctk.IntVar(value=int(task.get("concluida", 0)))
        self.completed_check = ctk.CTkCheckBox(
            self,
            text="",
            width=26,
            variable=self.completed_var,
            onvalue=1,
            offvalue=0,
            command=self._on_task_completed_toggle,
        )
        self.completed_check.grid(row=0, column=0, padx=(14, 8), pady=(14, 8), sticky="nw")

        title_color = "#7c8798" if self._is_done() else "#f8fbff"
        title_font = ctk.CTkFont(
            family="Segoe UI",
            size=16,
            weight="bold",
            overstrike=self._is_done(),
        )
        self.title_label = ctk.CTkLabel(
            self,
            text=task.get("title", "Task"),
            font=title_font,
            text_color=title_color,
            anchor="w",
        )
        self.title_label.grid(row=0, column=1, sticky="ew", pady=(14, 8))
        self.title_label.bind("<Button-1>", self._start_inline_edit)

        meta = ctk.CTkFrame(self, fg_color="transparent")
        meta.grid(row=0, column=2, padx=14, pady=(12, 8), sticky="e")

        priority = int(task.get("prioridade", 1) or 1)
        priority_text, priority_color = PRIORITY_LABELS.get(priority, PRIORITY_LABELS[1])
        self.priority_badge = ctk.CTkLabel(
            meta,
            text=priority_text,
            font=("Segoe UI", 11, "bold"),
            text_color="#0b1120",
            fg_color=priority_color,
            corner_radius=6,
            width=58,
            height=24,
        )
        self.priority_badge.grid(row=0, column=0, padx=(0, 8))

        self.status_btn = ctk.CTkButton(
            meta,
            text=self._status_label(),
            width=96,
            height=28,
            fg_color=self._status_color(),
            hover_color="#334155",
            command=self._on_status_cycle,
        )
        self.status_btn.grid(row=0, column=1)

        self.checks_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.checks_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 14))

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
            checkbox.pack(anchor="w", pady=4, fill="x")

        self.progress = ctk.CTkProgressBar(self, height=10)
        self.progress.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 14), pady=(10, 16))
        self._update_progress()
        
        self.bind("<Enter>", lambda e: self.configure(fg_color="#1f2937"))
        self.bind("<Leave>", lambda e: self.configure(fg_color="#111827"))

    def apply_task(self, task):
        self.task = task
        self.completed_var.set(int(task.get("concluida", 0)))
        self.title_label.configure(
            text=task.get("title", "Task"),
            text_color="#7c8798" if self._is_done() else "#f8fbff",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold",
                overstrike=self._is_done(),
            ),
        )
        self.status_btn.configure(text=self._status_label(), fg_color=self._status_color())

    def _start_inline_edit(self, _event=None):
        if self._editing:
            return
        self._editing = True
        self.title_label.grid_remove()
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.insert(0, self.task.get("title", ""))
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(12, 8))
        self.title_entry.focus()
        self.title_entry.select_range(0, "end")
        self.title_entry.bind("<Return>", self._save_inline_edit)
        self.title_entry.bind("<Escape>", self._cancel_inline_edit)
        self.title_entry.bind("<FocusOut>", self._save_inline_edit)

    def _save_inline_edit(self, _event=None):
        if not self._editing:
            return
        title = self.title_entry.get().strip()
        self.title_entry.destroy()
        self.title_label.grid()
        self._editing = False
        if not title or title == self.task.get("title"):
            return
        if self.on_title_save:
            updated = self.on_title_save(self.task["id"], title)
            if updated:
                self.apply_task(updated)

    def _cancel_inline_edit(self, _event=None):
        if not self._editing:
            return
        self.title_entry.destroy()
        self.title_label.grid()
        self._editing = False

    def _on_task_completed_toggle(self):
        if self.on_completed_toggle:
            updated = self.on_completed_toggle(self.task["id"], bool(self.completed_var.get()))
            if updated:
                self.apply_task(updated)

    def _on_status_cycle(self):
        if self.on_status_cycle:
            updated = self.on_status_cycle(self.task["id"])
            if updated:
                self.apply_task(updated)

    def _on_toggle(self, subtask, var):
        if self.on_subtask_toggle:
            updated = self.on_subtask_toggle(subtask["id"], bool(var.get()))
            if updated:
                self.apply_task(updated)
        else:
            task_manager.set_subtask_status(subtask["id"], bool(var.get()))
        self._update_progress()
        if self.on_progress_change:
            self.on_progress_change()

    def _update_progress(self):
        total = len(self._vars)
        completed = sum(var.get() for var in self._vars)
        progress = completed / total if total else 0
        self.progress.set(progress)

    def _is_done(self):
        return self.task.get("status") == "concluida" or int(self.task.get("concluida", 0)) == 1

    def _status_label(self):
        return STATUS_LABELS.get(self.task.get("status"), "Pendente")

    def _status_color(self):
        status = self.task.get("status")
        if status == "concluida":
            return "#16a34a"
        if status == "pausada":
            return "#ca8a04"
        return "#2563eb"


class CourseCard(ctk.CTkFrame):
    def __init__(self, master, task, course, on_progress_change=None, **kwargs):
        super().__init__(
            master,
            fg_color="#111827"  ,
            border_color="#263449",
            border_width=1,
            corner_radius=8,
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
            corner_radius=8,
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
