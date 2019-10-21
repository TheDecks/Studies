from typing import Tuple


class Cell:

    __possible_states = {'empty', 'tree', 'burning', 'burned'}
    _state: str

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.state = 'empty'
        self.ignite_probability = 0

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

    def add_ignition_probability(self, additional_prob: float):
        self.ignite_probability += additional_prob

    def __eq__(self, other: 'Cell'):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)
