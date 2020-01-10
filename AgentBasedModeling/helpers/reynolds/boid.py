from typing import Optional, Union

import math
import matplotlib.pyplot as plt
import matplotlib.patches as ptch


class Boid:

    size: float = 1
    width: float = 0.5

    def __init__(
            self,
            x: float, y: float,
            look_up_distance: float, look_up_angle: float,
            velocity: float, direction: float,
            species_name: Union[str, int] = 1
    ):
        """Create boid object in 2D-plane.

        :param x: x position.
        :param y: y position.
        :param look_up_distance: distance in which boid "sees". Also works as maximal velocity.
        :param look_up_angle: angle range of neighbourhood.
        :param velocity: starting velocity of void.
        :param direction: starting angle.
        :param species_name: name of species it belongs to.
        """
        self.x = x
        self.y = y

        self.v = velocity
        self.direction = direction

        self.lu_distance = look_up_distance
        self.lu_angle = look_up_angle

        self.species_name = species_name

    def sees(self, point_x: float, point_y: float, ang: Optional[float] = None, dist: Optional[float] = None) -> bool:
        """Check if point is in boids neighbourhood area.

        :param point_x: x position of point.
        :param point_y: y position of point.
        :param ang: seeing angle. Defaults to look up angle.
        :param dist: seeing distance. Defaults to look up distance.
        :return: flag saying if boid sees the point.
        """
        if ang is None:
            ang = self.lu_angle
        if dist is None:
            dist = self.lu_distance
        if dist ** 2 < (point_x - self.x) ** 2 + (point_y - self.y) ** 2:
            return False
        relative_point_angle = (math.atan2(point_y - self.y, point_x - self.x) - self.direction) % (2 * math.pi)
        if ang / 2 < relative_point_angle < 2 * math.pi - ang / 2:
            return False
        return True

    def change_speed(self, vel_x: float, vel_y: float):
        """Change current speed from cartesian vector.

        :param vel_x: x component of velocity vector.
        :param vel_y: y component of velocity vector.
        """
        v = math.sqrt(vel_x ** 2 + vel_y ** 2)
        if v > self.lu_distance:
            v = self.lu_distance
        angle = math.atan2(vel_y, vel_x) % (2 * math.pi)
        self.v = v
        self.direction = angle

    def move(self, limit: float):
        """Process boid according to it's velocity.

        :param limit: board size. Makes for boundary conditions.
        """
        v_x, v_y = math.cos(self.direction) * self.v, math.sin(self.direction) * self.v
        self.x += v_x
        self.y += v_y
        self.x = self.x % limit
        self.y = self.y % limit

    def draw(self, ax: plt.Axes, show_range: bool = False):
        """Draw boid on provided matplotlib axes object.

        :param ax: axes on which the boid should be drawn.
        :param show_range: whether to also show "seeing" range of the boid.
        """
        if show_range:
            arc = ptch.Arc(
                (self.x, self.y),
                width=2 * self.lu_distance,
                height=2 * self.lu_distance,
                angle=math.degrees(self.direction),
                theta1=math.degrees(2 * math.pi - self.lu_angle / 2),
                theta2=math.degrees(self.lu_angle / 2),
                color='black',
                linewidth=1,
                alpha=0.3,
                zorder=5
            )
            line_1 = plt.Line2D(
                [self.x + self.lu_distance * math.cos(self.lu_angle / 2 + self.direction), self.x],
                [self.y + self.lu_distance * math.sin(self.lu_angle / 2 + self.direction), self.y],
                color='black',
                linewidth=1,
                alpha=0.3,
                zorder=5
            )
            line_2 = plt.Line2D(
                [self.x + self.lu_distance * math.cos(2 * math.pi - self.lu_angle / 2 + self.direction), self.x],
                [self.y + self.lu_distance * math.sin(2 * math.pi - self.lu_angle / 2 + self.direction), self.y],
                color='black',
                linewidth=1,
                alpha=0.3,
                zorder=5
            )
            ax.add_line(line_1)
            ax.add_line(line_2)
            ax.add_patch(arc)
        ax.add_patch(self._arrow_representation())

    def _arrow_representation(self, colour: str = '#FF0000') -> ptch.FancyArrow:
        """Draw helper function. Represent boid as directed arrow with tip on boid's position."""
        dx = Boid.size * math.cos(self.direction)
        dy = Boid.size * math.sin(self.direction)
        arr = ptch.FancyArrow(
            x=self.x - dx,
            y=self.y - dy,
            dx=dx,
            dy=dy,
            length_includes_head=True,
            head_width=Boid.width,
            head_length=Boid.size,
            zorder=10,
            color=colour
        )
        return arr
