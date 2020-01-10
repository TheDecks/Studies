from typing import List, Tuple, Union, Optional
import math
import random
from AgentBasedModeling.helpers.reynolds import boid as b, obstacle as o, plotting_engine as pe


EPS = 10 ** -2


class ReynoldsModel:

    boids: List[b.Boid]
    obstacles: List[o.Obstacle]

    def __init__(
            self,
            board_size: float,
            separation_importance: float = 1,
            alignment_importance: float = 1,
            cohesion_importance: float = 1,
            avoid_distance: Optional[float] = None,
            obstacle_omit_edge_weight: float = 1,
            **kwargs
    ):
        """Initialize model and define basic properties.

        :param board_size: x and y size.
        :param separation_importance: coefficient of separation.
        :param alignment_importance: coefficient of alignment.
        :param cohesion_importance: coefficient of cohesion.
        :param avoid_distance:  distance at which boilds start to avoid themselves.
        :param obstacle_omit_edge_weight: how fast does direction of boid tend to obstacle edge.
        :param kwargs: plotting engine options.
        """
        self.board_size = board_size
        self.sep_coef = separation_importance
        self.align_coef = alignment_importance
        self.coh_coef = cohesion_importance
        if avoid_distance is None:
            avoid_distance = 2 * b.Boid.size
        self.boid_avoid_distance = avoid_distance
        self.obstacle_omit_edge_weight = obstacle_omit_edge_weight
        self.plotting_engine = pe.PlottingEngine(self.board_size, **kwargs)
        self.boids = []
        self.obstacles = []

    def add_obstacle(self, *points: Tuple[float, float]):
        """Add obstacle as polygon from points.

        :param points: points in form (x, y).
        """
        self.obstacles.append(o.Obstacle(*points))

    def is_in_obstacle(self, x: float, y: float) -> bool:
        """Check if point is in any obstacle.

        :param x: x position of point.
        :param y: y position of point.
        :return: contain test result.
        """
        for obstacle in self.obstacles:
            if obstacle.contains_point((x, y)):
                return True
        return False

    def add_boids(
            self,
            n: int,
            look_up_distance: float,
            look_up_angle: float,
            species_name: Union[str, int] = 1
    ):
        """Add boids onto board. For params definition look at boid help.
        """
        while n > 0:
            _x = random.random() * self.board_size
            _y = random.random() * self.board_size
            if self.is_in_obstacle(_x, _y):
                continue
            vel = random.random() * look_up_distance
            direction = random.random() * math.pi * 2
            self.boids.append(b.Boid(_x, _y, look_up_distance, look_up_angle, vel, direction, species_name))
            n -= 1

    def get_neighbours(self, boid: b.Boid) -> List[b.Boid]:
        """Get list of boids that boid can see.

        :param boid: boid whose neighbourhood is to be calculated.
        """
        neighbours = []
        for possible_neighbour in self.boids:
            if (
                possible_neighbour is not boid and
                possible_neighbour.species_name == boid.species_name and
                boid.sees(possible_neighbour.x, possible_neighbour.y)
            ):
                neighbours.append(possible_neighbour)
        return neighbours

    @staticmethod
    def calculate_cohesion(boids: List[b.Boid]) -> Tuple[float, float]:
        """Calculate center position of boids.
        """
        center_x = 0
        center_y = 0
        for boid in boids:
            center_x += boid.x
            center_y += boid.y
        return center_x / len(boids), center_y / len(boids)

    @staticmethod
    def calculate_alignment(boids: List[b.Boid]) -> Tuple[float, float]:
        """Calculate mean velocity vector of boids."""
        align_x = 0
        align_y = 0
        for boid in boids:
            align_x += boid.v * math.cos(boid.direction)
            align_y += boid.v * math.sin(boid.direction)
        return align_x / len(boids), align_y / len(boids)

    def calculate_separation(self, from_boid: b.Boid, boids: List[b.Boid]) -> Tuple[float, float]:
        """Calculate separation of from_boid, given boids list."""
        separation_x = 0
        separation_y = 0
        for boid in boids:
            distance_squared = (boid.x - from_boid.x) ** 2 + (boid.y - from_boid.y) ** 2
            if distance_squared < self.boid_avoid_distance:
                separation_x -= (boid.x - from_boid.x)
                separation_y -= (boid.y - from_boid.y)
        return separation_x, separation_y

    def move(self):
        """Precalculate velocities for all boids and assign them later. Change their course if they would run into
        obstacle. Finaly move boid."""
        new_velocities = self._create_velocities()
        for boid, vel in zip(self.boids, new_velocities):
            boid.change_speed(*vel)
            for obstacle in self.obstacles:
                self.boid_omit_obstacle(boid, obstacle)
            boid.move(self.board_size)

    def simulate(self, n: int, show_neighbourhood: bool = False):
        """Process the boids n times. Also save images."""
        self.draw_current_state(show_neighbourhood)
        for _ in range(n):
            self.move()
            self.draw_current_state(show_neighbourhood)
        self.plotting_engine.animate()

    def _create_velocities(self):
        """Calculate velocity for each boid, considering all basic rules."""
        velocities = []
        for boid in self.boids:
            neighbouring = self.get_neighbours(boid)
            boid_v_x = boid.v * math.cos(boid.direction)
            boid_v_y = boid.v * math.sin(boid.direction)
            if neighbouring:
                coh_x, coh_y = ReynoldsModel.calculate_cohesion(neighbouring)
                coh_x -= boid.x
                coh_y -= boid.y
                align_x, align_y = ReynoldsModel.calculate_alignment(neighbouring)
                sep_x, sep_y = self.calculate_separation(boid, neighbouring)
                velocities.append((
                    boid_v_x + self.coh_coef * coh_x + self.align_coef * align_x + self.sep_coef * sep_x,
                    boid_v_y + self.coh_coef * coh_y + self.align_coef * align_y + self.sep_coef * sep_y
                ))
            else:
                velocities.append((boid_v_x, boid_v_y))
        return velocities

    def boid_omit_obstacle(self, boid: b.Boid, obstacle: o.Obstacle):
        """Find closest edge of obstacle that boid can run into and change boids direction and velocity accordingly."""
        closest_distance = None
        omit_edge = None
        for edge in obstacle.edges():
            intersect = ReynoldsModel.boid_calculate_edge_intersect(boid, edge)
            if intersect is not None:
                intersect_x, intersect_y = intersect
                distance = math.sqrt((intersect_x - boid.x) ** 2 + (intersect_y - boid.y) ** 2)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    omit_edge = edge
        if closest_distance is not None:
            (p_1_x, p_1_y), (p_2_x, p_2_y) = omit_edge
            boid.v = closest_distance
            edge_angle = math.atan2(p_2_y - p_1_y, p_2_x - p_1_x) % (2 * math.pi)
            if abs(edge_angle - boid.direction) % (2 * math.pi) > math.pi / 2:
                edge_angle = edge_angle + math.pi
            boid.direction = (
                                     boid.direction + self.obstacle_omit_edge_weight * edge_angle
                             ) / (1 + self.obstacle_omit_edge_weight)
            if abs(boid.direction - edge_angle) < EPS:
                boid.direction = edge_angle
                boid.v = random.random() / 3 * boid.lu_distance

    @staticmethod
    def boid_calculate_edge_intersect(
            boid: b.Boid, edge: Tuple[Tuple[float, float], Tuple[float, float]]
    ) -> Optional[Tuple[float, float]]:
        """Find point of intersection between void velocity vector and given edge. None if they don't intersect.
        https://stackoverflow.com/a/565282/11894396 implemented."""

        obstacle_vel_x = boid.v * math.cos(boid.direction)
        obstacle_vel_y = boid.v * math.sin(boid.direction)

        (p_1_x, p_1_y), (p_2_x, p_2_y) = edge

        edge_offset_x = p_2_x - p_1_x
        edge_offset_y = p_2_y - p_1_y
        r_x_s = obstacle_vel_x * edge_offset_y - obstacle_vel_y * edge_offset_x

        if r_x_s == 0:
            return None
        else:
            t = (
                (p_1_x - boid.x) * edge_offset_y -
                (p_1_y - boid.y) * edge_offset_x
            ) / r_x_s
            u = (
                (p_1_x - boid.x) * obstacle_vel_y -
                (p_1_y - boid.y) * obstacle_vel_x
            ) / r_x_s
        if 0 < t < 1 and 0 < u < 1:
            intersect_x = p_1_x + u * edge_offset_x
            intersect_y = p_1_y + u * edge_offset_y
            return intersect_x, intersect_y
        else:
            return None

    def setup_plotting(self):
        """Prepare plotting object."""
        self.plotting_engine.remove_ticks()
        self.plotting_engine.handle_out_directory()

    def draw_current_state(self, show_neighbourhood: bool = False):
        """Process plotting."""
        self.plotting_engine.reset()
        for obstacle in self.obstacles:
            obstacle.draw(self.plotting_engine.axis)
        for boid in self.boids:
            boid.draw(self.plotting_engine.axis, show_neighbourhood)
        self.plotting_engine.save()


if __name__ == "__main__":
    """Possible run."""
    rm = ReynoldsModel(200)
    rm.setup_plotting()
    rm.add_boids(1200, 3, 14/8 * math.pi)
    rm.simulate(1, False)

