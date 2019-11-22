from typing import Tuple, Iterable, Set, Dict


class Cell:

    __possible_states = {'alive', 'dead'}
    _state: str
    neighbours: Set['Cell']

    def __init__(self, x: int, y: int, state: str):
        self.x = x
        self.y = y
        self.state = state
        self.neighbours = set()

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, set_val: Tuple[int, int]):
        self.x = set_val[0]
        self.y = set_val[1]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, set_val: str):
        if set_val in Cell.__possible_states:
            self._state = set_val
        else:
            raise ValueError('Invalid state {state} for cell.'.format(state=set_val))

    def add_neighbours(self, neighbours: Iterable['Cell']):
        self.neighbours.update(neighbours)

    def report_neighbours_state(self) -> Dict[str, int]:
        _d = {state: 0 for state in Cell.__possible_states}
        for c in self.neighbours:
            _d[c.state] += 1
        return _d

    def __eq__(self, other: 'Cell'):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        return '<cell at ({},{})>'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()
