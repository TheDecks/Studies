from typing import Tuple, Iterable, Set, Dict, Optional, Union


class Cell:

    agent: Optional[str]
    neighbours: Set['Cell']

    def __init__(self, x: int, y: int, agent: Optional[str] = None):
        self.x = x
        self.y = y
        self.agent = agent
        self.neighbours = set()

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, set_val: Tuple[int, int]):
        self.x = set_val[0]
        self.y = set_val[1]

    def add_neighbours(self, neighbours: Iterable['Cell']):
        self.neighbours.update(neighbours)

    def is_agent_happy(self, happiness_factor: int) -> bool:
        happiness_counter = 0
        other_counter = 0
        for c in self.neighbours:
            if c.agent == self.agent:
                happiness_counter += 1
            elif c.agent is not None:
                other_counter += 1
            if happiness_counter >= happiness_factor:
                return True
        if other_counter + happiness_counter == 0:
            return True
        return False

    def would_be_happy(self, agent_type: Union[int, str], happiness_factor: int):
        happiness_counter = 0
        other_counter = 0
        for c in self.neighbours:
            if c.agent == agent_type:
                happiness_counter += 1
            elif c.agent is not None:
                other_counter += 1
            if happiness_counter >= happiness_factor:
                return True
        if other_counter + happiness_counter == 0:
            return True
        return False

    def segregation_index(self):
        happiness_counter = 0
        other_counter = 0
        for c in self.neighbours:
            if c.agent == self.agent:
                happiness_counter += 1
            elif c.agent is not None:
                other_counter += 1
        if other_counter + happiness_counter == 0:
            return 1
        else:
            return happiness_counter / (other_counter + happiness_counter)

    def __eq__(self, other: 'Cell'):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        return '<cell at ({},{})>'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()
