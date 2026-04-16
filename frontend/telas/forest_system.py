from __future__ import annotations


class ForestSystem:
    def __init__(self) -> None:
        self.forest: list[str] = []

    def load_count(self, count: int) -> None:
        self.forest = ["🌲"] * max(0, count)

    def add_tree(self) -> None:
        self.forest.append("🌲")

    def get_forest(self) -> list[str]:
        return list(self.forest)

    def get_message(self) -> str:
        total = len(self.forest)
        if total == 0:
            return "Plante sua primeira árvore."
        if total < 3:
            return "Sua floresta está começando..."
        if total < 10:
            return "Sua floresta está crescendo 🌱"
        return "Sua floresta está prosperando 🌳"
