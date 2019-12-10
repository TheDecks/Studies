from typing import Tuple

from AnalysisOfUnstructuredData.helpers.tweet.place import Place
from math import pi, cos, asin, sqrt


class CirclePlace(Place):

    def __init__(self, name: str, middle_point: Tuple[float, float], radius: float):
        super(CirclePlace, self).__init__(name)
        self.mid = middle_point
        self.r = radius

    def contains_point(self, point: Tuple[float, float]) -> bool:
        lat1, lon1 = self.mid
        lat2, lon2 = point
        p = pi / 180
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a)) < self.r

    def contains_map_point(self, point: Tuple[float, float]) -> bool:
        return self.contains_point(point)

    def middle(self) -> Tuple[float, float]:
        return self.mid
