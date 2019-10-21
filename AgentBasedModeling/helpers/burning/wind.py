from typing import Tuple

import AgentBasedModeling.common.mclasses.singleton as singleton
import random
import math


class Wind(metaclass=singleton.Singleton):

    def __init__(
            self, initial_direction_angle: float = 0,
            initial_power: float = 0,
            is_randomized: bool = False
    ):
        self.direction = initial_direction_angle
        self.power = initial_power
        self.is_state_random = is_randomized

        self._power_swing = 0.6
        self._angle_swing = 60

    @property
    def power(self) -> float:
        return self._power

    @power.setter
    def power(self, set_val: float):
        if set_val > 1:
            self._power = 1
        elif set_val < 0:
            self._power = abs(set_val)
            self.direction = -1 * self.direction
        else:
            self._power = set_val

    @property
    def direction(self) -> float:
        return self._direction

    @direction.setter
    def direction(self, set_val: float):
        self._direction = set_val % 360

    def get_wind_propagation_center(self) -> Tuple[float, float]:
        vertical_shift = self.power * math.sin(2*math.pi*self.direction/360)
        horizontal_shift = self.power * math.cos(2*math.pi*self.direction/360)
        return horizontal_shift, vertical_shift

    def set_power_swing(self, swing: float):
        self._power_swing = swing

    def set_angle_swing(self, swing: float):
        self._angle_swing = swing

    def process(self):
        if self.is_state_random:
            to_add = random.random() * self._power_swing - self._power_swing / 2
            self.direction += random.random() * self._angle_swing - self._angle_swing / 2
            self.power += to_add
