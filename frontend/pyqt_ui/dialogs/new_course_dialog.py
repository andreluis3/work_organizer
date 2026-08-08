# frontend/pyqt_ui/dialogs/new_course_dialog.py
"""
Diálogo de criação de novo curso.

Migração do _CourseDialog (CustomTkinter), mesmo padrão do EventDialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class NewCourseDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo Curso")
        self.setMinimumSize(380, 260)
        self.setModal(True)

        self.result_title = ""
        self.result_total_lessons = 1

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        root.addWidget(QLabel("Nome do curso"))
        self.title_input = QLineEdit()
        root.addWidget(self.title_input)

        root.addWidget(QLabel("Total de aulas"))
        self.total_input = QLineEdit("10")
        root.addWidget(self.total_input)

        self.status_label = QLabel("")
        self.status_label.setObjectName("dialogStatus")
        root.addWidget(self.status_label)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        create_btn = QPushButton("Criar")
        create_btn.setObjectName("primaryButton")
        create_btn.clicked.connect(self._confirm)
        buttons_row.addWidget(cancel_btn)
        buttons_row.addWidget(create_btn)
        root.addLayout(buttons_row)

        self.title_input.setFocus()

    def _confirm(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            self.status_label.setText("O nome do curso nao pode ficar vazio.")
            return

        try:
            total = int(self.total_input.text().strip())
        except ValueError:
            total = 1

        self.result_title = title
        self.result_total_lessons = max(1, total)
        self.accept()