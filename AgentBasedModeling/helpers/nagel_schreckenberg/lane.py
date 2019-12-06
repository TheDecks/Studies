from typing import List

import AgentBasedModeling.helpers.nagel_schreckenberg.cell as c
import math


class Lane:

    cells: List[c.Cell]

    def __init__(self, number_of_cells: int, speed_limit: int):
        self.n = number_of_cells
        self.speed_limit = speed_limit
        self.cells = []

    def create_cells(self, r: float):
        angles = [i / self.n * 2 * math.pi for i in range(self.n)]
        self.cells = [c.Cell(r * math.cos(alpha), r * math.sin(alpha), i) for i, alpha in enumerate(angles)]

    def retrieve_previous_non_empty(self, position: int, max_behind: int) -> c.Cell:
        _i = 0
        for _i in range(max_behind):
            if not self.cells[position - 1 - _i].is_empty:
                break
        return self.cells[position - 1 - _i]

    def retrieve_furthest_empty(self, position: int, max_ahead: int) -> c.Cell:
        _i = 0
        for _i in range(max_ahead + 1):
            if not self.cells[(position + 1 + _i) % self.n].is_empty:
                break
        return self.cells[(position + _i) % self.n]

    def offset_cell(self, cell: c.Cell, offset: int = -1):
        return self.cells[(self.cells.index(cell) + offset) % self.n]
