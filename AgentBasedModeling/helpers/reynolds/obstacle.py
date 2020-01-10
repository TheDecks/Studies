from typing import Tuple, Generator
import matplotlib.pyplot as plt


class Obstacle:

    def __init__(self, *points: Tuple[float, float]):
        """Create obstacle as gathering of ordered points.

        :param points: Points in (x, y) form.
        """
        self.points = points

    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside polygon defined by points. Implements ray casting algorithm.
        https://en.wikipedia.org/wiki/Point_in_polygon

        :param point: point in form (x, y).
        :type point:
        :return: Contain test result.
        """
        x_p, y_p = point
        prev_x, prev_y = self.points[-1]
        contains = False
        for x, y in self.points:
            if (y < y_p <= prev_y or prev_y < y_p <= y) and prev_x <= x_p <= x:
                if x + (y_p - y)/(prev_y - y) * (prev_x - x) < x_p:
                    contains = not contains
            prev_x, prev_y = x, y
        return contains

    def edges(self) -> Generator[Tuple[Tuple[float, float], Tuple[float, float]], None, None]:
        """Returns consequent edges as a tuple of starting and ending point."""
        prev_point = self.points[-1]
        for point in self.points:
            yield prev_point, point
            prev_point = point

    def draw(self, ax: plt.Axes):
        """Add polygon as line onto matplotlib axes object."""
        _x = []
        _y = []
        for x, y in self.points:
            _x.append(x)
            _y.append(y)
        _x.append(self.points[0][0])
        _y.append(self.points[0][1])
        ax.plot(_x, _y)
