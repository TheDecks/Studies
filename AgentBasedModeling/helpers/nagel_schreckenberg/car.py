from typing import Optional

import AgentBasedModeling.helpers.nagel_schreckenberg.cell as c


class Car:

    _ID: int = 0
    next_cell: Optional[c.Cell]

    def __init__(self, starting_cell: c.Cell, lane: int, starting_velocity: int):
        self.id = Car._ID
        Car._ID += 1
        self.cell = starting_cell
        self.lane_no = lane
        self.velocity = starting_velocity
        self.next_cell = None

    def move(self):
        self.cell.is_empty = True
        self.next_cell.is_empty = False
        self.cell = self.next_cell
        self.next_cell = None

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
