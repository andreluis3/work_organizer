# frontend/pyqt_ui/widgets/tasks/course_card.py
"""
Card de um curso: progresso via slider, aula atual editável.

Widget "burro" com interação: emite `progress_updated` com os dados
necessários para persistir; nunca chama TaskController/ViewModel direto.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QSlider,
    QVBoxLayout,
)

from frontend.pyqt_ui.viewmodels.tasks_viewmodel import CourseCardData


class CourseCard(QFrame):
    progress_updated = pyqtSignal(int, int, str, int)
    """task_id, completed_lessons, current_lesson, total_lessons"""

    def __init__(self, data: CourseCardData, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("taskCard")
        self.data = data

        self._build_ui()
        self.update_data(data)

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setObjectName("taskTitle")
        root.addWidget(self.title_label)

        self.progress_label = QLabel()
        self.progress_label.setObjectName("courseProgressLabel")
        root.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("taskProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("courseSlider")
        self.slider.sliderReleased.connect(self._on_slider_released)
        root.addWidget(self.slider)

        lesson_row = QHBoxLayout()
        lesson_row.setSpacing(8)

        lesson_caption = QLabel("Aula atual")
        lesson_caption.setObjectName("courseLessonCaption")
        lesson_row.addWidget(lesson_caption)

        self.lesson_input = QLineEdit()
        self.lesson_input.setObjectName("courseLessonInput")
        self.lesson_input.editingFinished.connect(self._on_lesson_changed)
        lesson_row.addWidget(self.lesson_input, stretch=1)

        root.addLayout(lesson_row)

    # ------------------------------------------------------------------
    # Atualização de dados
    # ------------------------------------------------------------------

    def update_data(self, data: CourseCardData) -> None:
        self.data = data

        self.title_label.setText(data.title)
        self.progress_label.setText(f"Progresso: {data.progress_label}")
        self.progress_bar.setValue(int(data.progress * 100))

        self.slider.blockSignals(True)
        self.slider.setRange(0, data.total_lessons)
        self.slider.setValue(data.completed_lessons)
        self.slider.blockSignals(False)

        if self.lesson_input.text() != data.current_lesson:
            self.lesson_input.setText(data.current_lesson)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_slider_released(self) -> None:
        completed = self.slider.value()
        self._emit_progress(completed)

    def _on_lesson_changed(self) -> None:
        self._emit_progress(self.slider.value())

    def _emit_progress(self, completed_lessons: int) -> None:
        current_lesson = self.lesson_input.text().strip() or "Aula 1"
        self.progress_updated.emit(
            self.data.id,
            completed_lessons,
            current_lesson,
            self.data.total_lessons,
        )