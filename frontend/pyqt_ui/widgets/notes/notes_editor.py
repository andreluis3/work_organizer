"""
Editor de Notes: QTextEdit + highlighting Markdown-lite (H1/H2/checkbox/
código), atalhos (Ctrl+B/I/K/Shift+C) e menu slash "/".

Fase 1: não oculta sintaxe (isso é Fase 2 — WYSIWYG real). O highlighting
já dá leitura visual próxima de WYSIWYG sem precisar de painel de preview.
"""

from __future__ import annotations

import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeySequence,
    QShortcut,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import QFrame, QListWidget, QListWidgetItem, QTextEdit, QVBoxLayout

SLASH_COMMANDS = [
    ("/h1", "Titulo grande", "# "),
    ("/h2", "Titulo medio", "## "),
    ("/todo", "Checklist item", "- [ ] "),
    ("/list", "Lista com marcadores", "- "),
    ("/code", "Bloco de codigo", "```\n\n```"),
]


class _MarkdownLiteHighlighter(QSyntaxHighlighter):
    CODE_BLOCK_STATE = 1

    def __init__(self, document) -> None:
        super().__init__(document)
        self._h1 = self._make_format("#22C55E", bold=True, size=16)
        self._h2 = self._make_format("#38BDF8", bold=True, size=14)
        self._checkbox = self._make_format("#94A3B8")
        self._code = self._make_format("#E5E7EB", background="#111827", family="JetBrains Mono")
        self._bold = self._make_format(None, bold=True)
        self._italic = self._make_format(None, italic=True)

        self._checkbox_re = re.compile(r"^\s*- \[ \]")
        self._bold_re = re.compile(r"\*\*(.+?)\*\*")
        self._italic_re = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")

    def _make_format(self, color, background=None, bold=False, italic=False, size=None, family=None):
        fmt = QTextCharFormat()
        if color:
            fmt.setForeground(QColor(color))
        if background:
            fmt.setBackground(QColor(background))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        if size:
            fmt.setFontPointSize(size)
        if family:
            fmt.setFontFamily(family)
        return fmt

    def highlightBlock(self, text: str) -> None:
        in_code = self.previousBlockState() == self.CODE_BLOCK_STATE
        stripped = text.strip()

        if stripped.startswith("```"):
            self.setFormat(0, len(text), self._code)
            self.setCurrentBlockState(0 if in_code else self.CODE_BLOCK_STATE)
            return

        if in_code:
            self.setFormat(0, len(text), self._code)
            self.setCurrentBlockState(self.CODE_BLOCK_STATE)
            return

        self.setCurrentBlockState(0)

        if text.startswith("# "):
            self.setFormat(0, len(text), self._h1)
            return
        if text.startswith("## "):
            self.setFormat(0, len(text), self._h2)
            return

        checkbox_match = self._checkbox_re.match(text)
        if checkbox_match:
            self.setFormat(checkbox_match.start(), checkbox_match.end() - checkbox_match.start(), self._checkbox)

        for match in self._bold_re.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self._bold)
        for match in self._italic_re.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self._italic)


class _SlashMenu(QFrame):
    def __init__(self, parent: QTextEdit) -> None:
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.setObjectName("slashMenu")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("slashMenuList")
        for label, description, _snippet in SLASH_COMMANDS:
            self.list_widget.addItem(QListWidgetItem(f"{label}   {description}"))
        self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        self.setFixedWidth(240)


class NotesEditor(QTextEdit):
    content_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("notesEditor")
        self.setAcceptRichText(False)

        font = QFont("JetBrains Mono")
        font.setPointSize(11)
        self.setFont(font)

        self._highlighter = _MarkdownLiteHighlighter(self.document())
        self._slash_menu = _SlashMenu(self)
        self._slash_start: int | None = None

        self.textChanged.connect(lambda: self.content_changed.emit(self.toPlainText()))
        self._install_shortcuts()

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+B"), self, activated=lambda: self._wrap_selection("**", "**"))
        QShortcut(QKeySequence("Ctrl+I"), self, activated=lambda: self._wrap_selection("*", "*"))
        QShortcut(QKeySequence("Ctrl+K"), self, activated=lambda: self._wrap_selection("[", "](url)"))
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, activated=lambda: self._wrap_selection("`", "`"))

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_content(self, text: str) -> None:
        self.blockSignals(True)
        self.setPlainText(text)
        self.blockSignals(False)

    def get_content(self) -> str:
        return self.toPlainText()

    # ------------------------------------------------------------------
    # Atalhos de formatação
    # ------------------------------------------------------------------

    def _wrap_selection(self, prefix: str, suffix: str) -> None:
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            for _ in range(len(suffix)):
                cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)

    # ------------------------------------------------------------------
    # Menu slash
    # ------------------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        if self._slash_menu.isVisible():
            if event.key() == Qt.Key.Key_Down:
                self._move_slash_selection(1)
                return
            if event.key() == Qt.Key.Key_Up:
                self._move_slash_selection(-1)
                return
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._confirm_slash_selection()
                return
            if event.key() == Qt.Key.Key_Escape:
                self._close_slash_menu()
                return

        super().keyPressEvent(event)

        if event.text() == "/":
            self._open_slash_menu()
        elif self._slash_menu.isVisible():
            self._close_slash_menu()

    def _open_slash_menu(self) -> None:
        self._slash_start = self.textCursor().position()
        global_pos = self.viewport().mapToGlobal(self.cursorRect().bottomLeft())
        self._slash_menu.move(global_pos)
        self._slash_menu.list_widget.setCurrentRow(0)
        self._slash_menu.show()

    def _close_slash_menu(self) -> None:
        self._slash_menu.hide()
        self._slash_start = None

    def _move_slash_selection(self, step: int) -> None:
        list_widget = self._slash_menu.list_widget
        next_row = (list_widget.currentRow() + step) % list_widget.count()
        list_widget.setCurrentRow(next_row)

    def _confirm_slash_selection(self) -> None:
        if self._slash_start is None:
            self._close_slash_menu()
            return

        row = self._slash_menu.list_widget.currentRow()
        _, _, snippet = SLASH_COMMANDS[row]

        cursor = self.textCursor()
        cursor.setPosition(self._slash_start - 1)
        cursor.setPosition(self._slash_start, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(snippet)

        self._close_slash_menu()