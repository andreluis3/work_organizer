# frontend/pyqt_ui/dialogs/new_task_dialog.py
"""
Diálogo de criação de nova task.

Migração do _TaskDialog (CustomTkinter), seguindo o mesmo padrão do
EventDialog da Agenda: QDialog autocontido, sem regra de negócio — apenas
coleta os campos e expõe via propriedades após accept().
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

PRIORITY_OPTIONS = {"Alta": 3, "Media": 2, "Baixa": 1}


class NewTaskDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nova Task")
        self.setMinimumSize(420, 460)
        self.setModal(True)

        self.result_title = ""
        self.result_subtasks: list[str] = []
        self.result_priority = 1

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        root.addWidget(QLabel("Titulo"))
        self.title_input = QLineEdit()
        root.addWidget(self.title_input)

        root.addWidget(QLabel("Prioridade"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(list(PRIORITY_OPTIONS.keys()))
        self.priority_combo.setCurrentText("Baixa")
        root.addWidget(self.priority_combo)

        root.addWidget(QLabel("Subtasks (uma por linha)"))
        self.subtasks_input = QTextEdit()
        self.subtasks_input.setFixedHeight(140)
        root.addWidget(self.subtasks_input)

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
            self.status_label.setText("O titulo nao pode ficar vazio.")
            return

        self.result_title = title
        self.result_subtasks = [
            line.strip() for line in self.subtasks_input.toPlainText().splitlines() if line.strip()
        ]
        self.result_priority = PRIORITY_OPTIONS.get(self.priority_combo.currentText(), 1)
        self.accept()