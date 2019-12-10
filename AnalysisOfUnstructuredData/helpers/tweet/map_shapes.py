from typing import Tuple, List

from AnalysisOfUnstructuredData.helpers.tweet import shapes


def square(name: str, left_bottom_point: Tuple[float, float], length: float):
    x, y = left_bottom_point
    x, y = x + 90, y + 180
    return shapes.square(name, (x, y), length)


def rectangle(
        name: str, left_bottom_point: Tuple[float, float], right_upper_point: Tuple[float, float]):
    x, y = left_bottom_point
    left_bottom_point = (x + 90, y + 180)
    x, y = right_upper_point
    right_upper_point = (x + 90, y + 180)
    return shapes.rectangle(name, left_bottom_point, right_upper_point)


def polygon(name: str, points: List[Tuple[float, float]]):
    points = [(x + 90, y + 180) for x, y in points]
    return shapes.polygon(name, points)


def circle(name: str, middle: Tuple[float, float], radius: float):
    return shapes.circle(name, middle, radius)
