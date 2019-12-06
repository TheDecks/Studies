from typing import Tuple


class Cell:

    def __init__(self, x: float, y: float, pos: int):
        self.x = x
        self.y = y
        self.pos = pos
        self.is_empty = True

    @property
    def position(self) -> Tuple[float, float]:
        return self.x, self.y

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)
