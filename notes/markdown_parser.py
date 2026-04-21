from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import re

import markdown


class _PlainTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._list_depth = 0
        self._in_pre = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"h1", "h2", "h3", "h4", "p", "pre", "blockquote"}:
            self.parts.append("\n")
        if tag in {"ul", "ol"}:
            self._list_depth += 1
            self.parts.append("\n")
        if tag == "li":
            indent = "  " * max(0, self._list_depth - 1)
            self.parts.append(f"{indent}- ")
        if tag == "br":
            self.parts.append("\n")
        if tag == "code":
            self.parts.append("`" if not self._in_pre else "")
        if tag == "pre":
            self._in_pre = True
            self.parts.append("```" + "\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4", "p", "blockquote"}:
            self.parts.append("\n")
        if tag in {"ul", "ol"}:
            self._list_depth = max(0, self._list_depth - 1)
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("\n")
        if tag == "code":
            self.parts.append("`" if not self._in_pre else "")
        if tag == "pre":
            self.parts.append("\n```" + "\n")
            self._in_pre = False

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        text = unescape("".join(self.parts))
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def _fallback_render(texto: str) -> str:
    text = texto or ""
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"```(\w+)?", "```", text)
    return text.strip()


def render_markdown(texto: str) -> str:
    source = texto or ""
    if not source.strip():
        return ""

    try:
        html = markdown.markdown(
            source,
            extensions=["fenced_code", "tables", "sane_lists"],
            output_format="html5",
        )
        parser = _PlainTextHTMLParser()
        parser.feed(html)
        rendered = parser.get_text()
        return rendered or _fallback_render(source)
    except Exception:
        return _fallback_render(source)
