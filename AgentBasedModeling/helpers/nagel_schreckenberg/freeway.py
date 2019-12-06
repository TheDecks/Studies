from typing import List, Set, Dict, Optional

import math
import random

from AgentBasedModeling.helpers.nagel_schreckenberg import lane as l, car as c, plotting_engine as pe


class Freeway:

    lanes: List[l.Lane]
    cars: Set[c.Car]
    cells_cars: Dict[l.c.Cell, c.Car]
    plotting_engine: Optional[pe.PlottingEngine]

    def __init__(
            self,
            slow_down_p: float,
            cars_density: float,
            lane_length: int,
            number_of_lanes: int = 1,
            speed_limit: int = 5,
            overtake_increase: bool = False,
            plot: bool = False,
            **kwargs
    ):
        self.p = slow_down_p
        self.rho = cars_density
        self.lanes_n = number_of_lanes
        self.lane_length = lane_length
        self.v_limit = speed_limit
        self.overtake_increase = overtake_increase
        self.lanes = []
        self.cars = set()
        self.cells_cars = {}
        self.next_step_taken = set()
        if plot:
            self.plotting_engine = pe.PlottingEngine(self.lanes_n, self.lane_length / 2 / math.pi, **kwargs)
            self.plotting_engine.handle_out_directory()
            self.plotting_engine.setup_base_axes()
            self.plotting_engine.setup_velocity_axes()
        else:
            self.plotting_engine = None

    @property
    def mean_velocity(self):
        if self.cars:
            return sum([car.velocity for car in self.cars]) / len(self.cars)
        return 0

    def build_lanes(self):
        _r = self.lane_length / 2 / math.pi
        for _i in range(self.lanes_n):
            lane = l.Lane(self.lane_length, self.v_limit + self.overtake_increase * _i)
            lane.create_cells(_r + _i)
            self.lanes.append(lane)

    def release_the_cars(self, no_lanes: int):
        for i, lane in enumerate(self.lanes[:no_lanes]):
            for cell in lane.cells:
                if random.random() < self.rho:
                    car = c.Car(cell, i, random.randint(0, self.v_limit))
                    cell.is_empty = False
                    self.cars.add(car)
                    self.cells_cars[cell] = car

    def process_plotting(self):
        if self.plotting_engine is not None:
            self.plotting_engine.clear_main_axes()
            self.plotting_engine.process_velocity_axes(self.mean_velocity)
            for car in self.cars:
                self.plotting_engine.draw_circle(car.cell.position, car.id, "red", 1)
            self.plotting_engine.save()

    def process(self):
        self.process_plotting()
        for car in self.cars:
            if car.velocity < self.lanes[car.lane_no].speed_limit:
                car.velocity += 1
            self.find_position_to_move(car)
        for car in self.cars:
            car.velocity = (car.next_cell.pos - car.cell.pos) % self.lane_length
            del self.cells_cars[car.cell]
            self.cells_cars[car.next_cell] = car
            car.move()
        self.next_step_taken = set()

    def find_position_to_move(self, car: c.Car):
        moves = [self._try_merge, self._try_overtake, self._move_current_lane]
        for move_possibility in moves:
            if car.next_cell is not None:
                break
            move_possibility(car)

    def _try_merge(self, car: c.Car):
        if car.lane_no > 0:
            merge_lane = self.lanes[car.lane_no - 1]
            curr_pos = car.cell.pos
            true_veloc = 1 if car.velocity == 0 else car.velocity - 1
            future_max_cell_ahead = merge_lane.retrieve_furthest_empty(curr_pos, true_veloc)
            merge_lane_previous = merge_lane.retrieve_previous_non_empty(
                curr_pos + 1, merge_lane.speed_limit + 1 - true_veloc
            )
            if merge_lane_previous in self.cells_cars:
                previous_car = self.cells_cars[merge_lane_previous]
                previous_max_ahead = previous_car.cell.pos + previous_car.velocity
            else:
                previous_max_ahead = curr_pos - 1
            if (
                    (future_max_cell_ahead.pos - previous_max_ahead) % self.lane_length
                    <= self.lanes[car.lane_no].speed_limit
            ):
                if future_max_cell_ahead not in self.next_step_taken and future_max_cell_ahead not in self.cells_cars:
                    car.next_cell = future_max_cell_ahead
                    car.lane_no -= 1
                    self.next_step_taken.add(car.next_cell)

    def _try_overtake(self, car: c.Car):
        if car.lane_no + 1 < self.lanes_n:
            this_lane_max_ahead = self.lanes[car.lane_no].retrieve_furthest_empty(car.cell.pos, car.velocity)
            if (this_lane_max_ahead.pos - car.cell.pos) % self.lane_length >= car.velocity:
                return
            this_lane_previous = (
                self.lanes[car.lane_no].retrieve_previous_non_empty(car.cell.pos, self.lanes[car.lane_no].speed_limit)
            )
            if this_lane_previous in self.cells_cars:
                if (
                        self.cells_cars[this_lane_previous].velocity >
                        (car.cell.pos - this_lane_previous.pos) % self.lane_length
                ):
                    return
            overtake_lane = self.lanes[car.lane_no + 1]
            curr_pos = car.cell.pos
            true_veloc = min(car.velocity + 1, overtake_lane.speed_limit)
            future_max_cell_ahead = overtake_lane.retrieve_furthest_empty(curr_pos, true_veloc)
            overtake_lane_previous = overtake_lane.retrieve_previous_non_empty(
                curr_pos + 1, overtake_lane.speed_limit + 1 - true_veloc
            )
            if overtake_lane_previous in self.cells_cars:
                previous_car = self.cells_cars[overtake_lane_previous]
                previous_max_ahead = previous_car.cell.pos + previous_car.velocity
            else:
                previous_max_ahead = curr_pos - 1
            if (
                    (future_max_cell_ahead.pos - previous_max_ahead) % self.lane_length
                    <= self.lanes[car.lane_no].speed_limit + 1
            ):
                if future_max_cell_ahead not in self.next_step_taken and future_max_cell_ahead not in self.cells_cars:
                    car.next_cell = future_max_cell_ahead
                    car.lane_no += 1
                    self.next_step_taken.add(car.next_cell)

    def _move_current_lane(self, car: c.Car):
        car.next_cell = self.lanes[car.lane_no].retrieve_furthest_empty(car.cell.pos, car.velocity)
        if random.random() < self.p and car.next_cell != car.cell:
            car.next_cell = self.lanes[car.lane_no].offset_cell(car.next_cell)
        if car.next_cell in self.next_step_taken:
            car.next_cell = car.cell
        self.next_step_taken.add(car.next_cell)

    def run(self, no_steps: int):
        for _ in range(no_steps):
            self.process()

    def animate(self):
        if self.plotting_engine is not None:
            self.plotting_engine.animate()


if __name__ == "__main__":
    f = Freeway(0.3, 0.6, 100, 1, 5, True, True)
    f.build_lanes()
    f.release_the_cars(1)
    f.run(50)
    f.animate()
