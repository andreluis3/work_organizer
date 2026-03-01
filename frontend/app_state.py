from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppState:
    current_screen: str = "dashboard"
    sidebar_collapsed: bool = False
    theme: str = "dark"
    notifications_enabled: bool = True
    data_cache: dict[str, Any] = field(default_factory=dict)
