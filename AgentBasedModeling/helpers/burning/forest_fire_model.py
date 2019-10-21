import decimal
from typing import Dict, Tuple, Set, Optional

import AgentBasedModeling.helpers.burning.cell as cell
import AgentBasedModeling.helpers.burning.wind as wind
import AgentBasedModeling.helpers.burning.plt_engine as pe
import AgentBasedModeling.common.log.logger_dec as ld
import AgentBasedModeling.common.log.logger as logger

import random

LOGGER = logger.get_logger(__name__)


class ForestFireModel:

    class IgnitionSpot:

        def __init__(self, x: float, y: float, parent_fire_model: 'ForestFireModel'):
            self.x = x
            self.y = y
            self._parent = parent_fire_model

        def propagate_ignition_probabilities(self):
            for cell_pos in self._find_effected_cells():
                self._parent.cells[cell_pos].add_ignition_probability(self._calculate_ignition_probability(cell_pos))

        def _find_effected_cells(self):
            x_effect_range = range(
                int(decimal.Decimal(self.x - 1.5).to_integral_value(rounding=decimal.ROUND_HALF_UP)),
                int(decimal.Decimal(self.x + 1.5).to_integral_value(rounding=decimal.ROUND_HALF_DOWN)) + 1
            )
            y_effect_range = range(
                int(decimal.Decimal(self.y - 1.5).to_integral_value(rounding=decimal.ROUND_HALF_UP)),
                int(decimal.Decimal(self.y + 1.5).to_integral_value(rounding=decimal.ROUND_HALF_DOWN)) + 1
            )
            return {(x, y) for x in x_effect_range for y in y_effect_range}.intersection(self._parent.cells.keys())

        def _calculate_ignition_probability(self, cell_pos: Tuple[int, int]):
            cell_x, cell_y = cell_pos
            # dx, dy = wind.Wind().get_wind_propagation_center()
            if cell_x - 0.5 < self.x - 1.5:
                x_length = cell_x + 2 - self.x
            elif cell_x + 0.5 > self.x + 1.5:
                x_length = self.x + 2 - cell_x
            else:
                x_length = 1
            if cell_y - 0.5 < self.y - 1.5:
                y_length = cell_y + 2 - self.y
            elif cell_y + 0.5 > self.y + 1.5:
                y_length = self.y + 2 - cell_y
            else:
                y_length = 1
            return x_length * y_length

        def __eq__(self, other):
            return (self.x, self.y) == (other.x, other.y)

        def __hash__(self):
            return hash((self.x, self.y))

    _plant_prob: float
    cells: Dict[Tuple[int, int], cell.Cell]
    non_empty_cells: Set[cell.Cell]
    _ignition_spots: Set[IgnitionSpot]
    _plotting_engine: Optional[pe.PlottingEngine]

    def __init__(
            self, lattice_size: int, tree_plant_probability: float, plotting_engine: Optional[pe.PlottingEngine] = None
    ):
        self.edge_length = lattice_size
        self.plant_prob = tree_plant_probability
        self.cells = {}
        self._time_counter = 0
        self.non_empty_cells = set()
        self._ignition_spots = set()
        self.plotting_engine = plotting_engine

    @property
    def plant_prob(self):
        return self._plant_prob

    @plant_prob.setter
    def plant_prob(self, set_val: float):
        if set_val < 0:
            self._plant_prob = 0
        elif set_val > 1:
            self._plant_prob = 1
        else:
            self._plant_prob = set_val

    @property
    def plotting_engine(self):
        return self._plotting_engine

    @plotting_engine.setter
    def plotting_engine(self, eng: Optional[pe.PlottingEngine]):
        if eng is None:
            self._plotting_engine = None
        else:
            self._plotting_engine = eng
            self._plotting_engine.prepare(self.plant_prob)

    def propagate_trees_to_plotting_engine(self):
        if self.plotting_engine is not None:
            self.plotting_engine.initialize_trees_places(self.non_empty_cells)
            self.plotting_engine.draw_trees(self.non_empty_cells)

    def process_plotting_engine(self):
        if self.plotting_engine is not None:
            self.plotting_engine.clear_main_axes()
            self.plotting_engine.draw_burning(self.burning)
            self.plotting_engine.draw_burned(self.burned)
            self.plotting_engine.draw_fire_propagation_range({
                (ig.x, ig.y) for ig in self._ignition_spots
            })
            self.plotting_engine.draw_wind_arrow()
            self.plotting_engine.save()

    @property
    def living(self) -> Set[cell.Cell]:
        return {cel for cel in self.non_empty_cells if cel.state == 'tree'}

    @property
    def burning(self) -> Set[cell.Cell]:
        return {cel for cel in self.non_empty_cells if cel.state == 'burning'}

    @property
    def burned(self) -> Set[cell.Cell]:
        return {cel for cel in self.non_empty_cells if cel.state == 'burned'}

    def create_cells(self):
        self.cells = {(x, y): cell.Cell(x, y) for x in range(self.edge_length) for y in range(self.edge_length)}

    def plant_trees(self):
        for pos in self.cells:
            if random.random() <= self.plant_prob:
                self.cells[pos].state = 'tree'
                self.non_empty_cells.add(self.cells[pos])
        self.propagate_trees_to_plotting_engine()

    def start_fire(self):
        for x in range(self.edge_length):
            if self.cells[(x, 0)].state == 'tree':
                self.cells[(x, 0)].state = 'burning'

    def spread(self):
        i_spots_x_offset, i_spots_y_offset = wind.Wind().get_wind_propagation_center()
        currently_burning = self.burning
        self._ignition_spots = {
            ForestFireModel.IgnitionSpot(cel.x + i_spots_x_offset, cel.y + i_spots_y_offset, self)
            for cel in currently_burning
        }
        self.process_plotting_engine()
        for spot in self._ignition_spots:
            spot.propagate_ignition_probabilities()
        for cel in self.non_empty_cells:
            if cel.state == 'tree':
                if random.random() <= cel.ignite_probability:
                    cel.state = 'burning'
                cel.ignite_probability = 0
        for cel in currently_burning:
            cel.state = 'burned'
        wind.Wind().process()
        self._time_counter += 1

    def burn(self):
        while self.burning:
            self.spread()
        if self.plotting_engine is not None:
            self._ignition_spots = set()
            self.process_plotting_engine()
            self.plotting_engine.animate()

    @property
    def is_top_hit(self) -> bool:
        return bool({
            cel for cel in self.non_empty_cells if cel.position[1] == self.edge_length - 1
        }.intersection(self.burned))

    @ld.debug_timer_dec(logger=LOGGER)
    def find_biggest_cluster_by_me(self, in_state: str = 'burned') -> int:

        def get_neighbouring_positions(pos: Tuple[int, int]):
            x, y = pos
            return {(x + 1, y), (x - 1, y), (x, y+1), (x, y - 1)}

        occupied = {pos for pos, cel in self.cells.items() if cel.state == in_state}
        clusters_found = 1
        clusters_counter = {}
        cell_queue = []
        while cell_queue or occupied:
            if not cell_queue:
                cell_queue.append(occupied.pop())
                clusters_found += 1
                clusters_counter[clusters_found] = 0
            curr_cell = cell_queue.pop()
            clusters_counter[clusters_found] += 1
            for pos in get_neighbouring_positions(curr_cell).intersection(occupied):
                cell_queue.append(pos)
                occupied.remove(pos)
        if not clusters_counter:
            return 0
        return max(clusters_counter.values())

    @ld.debug_timer_dec(logger=LOGGER)
    def find_biggest_cluster_by_kh(self, in_state = 'burned') -> int:

        def get_neighbouring_positions(cel: cell.Cell):
            x, y = cel.position
            return {(x + 1, y), (x - 1, y), (x, y+1), (x, y - 1)}

        max_cluster = 0
        cell_clusters = {}

        for x in range(self.edge_length):
            for y in range(self.edge_length):
                if self.cells[(x, y)].state == in_state:
                    neighbouring_clusters = {
                        cell_clusters[pos] for pos in get_neighbouring_positions(self.cells[(x, y)])
                        if pos in cell_clusters
                    }
                    if not neighbouring_clusters:
                        max_cluster += 1
                        cell_clusters[(x, y)] = max_cluster
                    elif len(neighbouring_clusters) == 1:
                        cell_clusters[(x, y)] = neighbouring_clusters.pop()
                    else:
                        group = neighbouring_clusters.pop()
                        cell_clusters[(x, y)] = group
                        cell_clusters = {
                            pos: group if cluster in neighbouring_clusters else cluster
                            for pos, cluster in cell_clusters.items()
                        }
        cluster_counts = {}
        for cluster in cell_clusters.values():
            if cluster not in cluster_counts:
                cluster_counts[cluster] = 1
            else:
                cluster_counts[cluster] += 1
        if not cluster_counts:
            return 0
        return max(cluster_counts.values())

    def restore(self):
        for cel in self.non_empty_cells:
            cel.state = 'tree'


if __name__ == '__main__':
    import time

    timing1 = 0
    timing2 = 0

    for _ in range(100):
        fire = ForestFireModel(
            50, 0.55, None
        )
        fire.create_cells()
        fire.plant_trees()
        fire.start_fire()
        fire.burn()
        snap = time.time()
        fire.find_biggest_cluster_by_me()
        timing1 += time.time() - snap
        snap = time.time()
        fire.find_biggest_cluster_by_kh()
        timing2 += time.time() - snap
    print(timing1)  # 0.476 s
    print(timing2)  # 3.295 s
