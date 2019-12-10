import abc
from typing import Tuple


class Place(abc.ABC):

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def contains_point(self, point: Tuple[float, float]) -> bool: ...

    def contains_map_point(self, point: Tuple[float, float]) -> bool:
        return self.contains_point((point[0] + 90, point[1] + 180))
