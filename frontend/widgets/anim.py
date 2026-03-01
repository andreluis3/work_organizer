from __future__ import annotations


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend_color(from_hex: str, to_hex: str, t: float) -> str:
    start = _hex_to_rgb(from_hex)
    end = _hex_to_rgb(to_hex)
    value = tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
    return _rgb_to_hex(value)
