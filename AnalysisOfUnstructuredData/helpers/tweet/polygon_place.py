from typing import Tuple, List

from AnalysisOfUnstructuredData.helpers.tweet.place import Place


class PolygonPlace(Place):

    def __init__(self, name: str, points: List[Tuple[float, float]]):
        super(PolygonPlace, self).__init__(name)
        self.points = points

    def contains_point(self, point: Tuple[float, float]) -> bool:
        x_p, y_p = point
        prev_x, prev_y = self.points[-1]
        contains = False
        for x, y in self.points:
            if (y < y_p <= prev_y or prev_y < y_p <= y) and prev_x <= x <= x_p:
                if x + (y_p - y)/(prev_y - y) * (prev_x - x) < x_p:
                    contains = not contains
        return contains
