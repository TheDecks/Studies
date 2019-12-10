from typing import Tuple, List
from AnalysisOfUnstructuredData.helpers.tweet.polygon_place import PolygonPlace
from AnalysisOfUnstructuredData.helpers.tweet.circle_place import CirclePlace


def square(name: str, left_bottom_point: Tuple[float, float], length: float) -> PolygonPlace:
    x, y = left_bottom_point
    points = [(x, y), (x + length, y), (x, y + length), (x + length, y + length)]
    return PolygonPlace(name, points)


def rectangle(
        name: str, left_bottom_point: Tuple[float, float], right_upper_point: Tuple[float, float]) -> PolygonPlace:
    x_off = right_upper_point[0] - left_bottom_point[0]
    y_off = right_upper_point[1] - left_bottom_point[1]
    x, y = left_bottom_point
    points = [left_bottom_point, right_upper_point, (x + x_off, y), (x, y + y_off)]
    return PolygonPlace(name, points)


def polygon(name: str, points: List[Tuple[float, float]]) -> PolygonPlace:
    return PolygonPlace(name, points)


def circle(name: str, middle: Tuple[float, float], radius: float) -> CirclePlace:
    return CirclePlace(name, middle, radius)
