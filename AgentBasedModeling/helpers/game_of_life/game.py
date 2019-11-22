from typing import Union, Iterable, Tuple, Dict, Set, Optional, Any

import numpy as np

from AgentBasedModeling.helpers.game_of_life import cell, plt_engine as pe
from AgentBasedModeling.common.log import logger
import os

LOGGER = logger.get_logger(__name__)


class GameOfLife:

    borders_names = ['bottom', 'top', 'left', 'right']
    borders_numbers = [1, 2, 3, 4]
    borders_name_number_mapping = {name: number for name, number in zip(borders_names, borders_numbers)}

    height: int
    width: int
    cells: Set[cell.Cell]
    game_state: Dict[cell.Cell, str]
    initial_state: Dict[cell.Cell, str]
    neighbours_shifts: Set[Tuple[int, int]]
    _reproduction_low: int
    _reproduction_high: int
    plotting_engine: Optional[pe.PlottingEngine]
    _portals: Set[int]

    def __init__(
            self, initial_state: Union[np.ndarray, Iterable[Iterable[int]]],
            neighbourhood_matrix: Optional[Union[np.ndarray, Iterable[Iterable[int]]]] = None,
            teleport_borders: Iterable[Union[str, int]] = (),
            underpopulation_threshold: int = 2, overpopulation_threshold: int = 3,
            reproduction_range: Union[Tuple[int, int], int] = 3,
            plot: bool = True, **kwargs
    ):
        try:
            self.size = initial_state.shape
        except AttributeError:
            self.size = (len(initial_state), len(initial_state[0]))

        self.game_state = {}
        self.cells = set()
        for x in range(self.width):
            for y in range(self.height):
                try:
                    c = cell.Cell(x, y, 'alive' if initial_state[self.height - 1 - y][x] == 1 else 'dead')
                    self.cells.add(c)
                    self.game_state[c] = c.state
                except IndexError as e:
                    LOGGER.error('Incompatible initial state size. Possibly rows have varying length.')
                    raise e

        self.initial_state = self.game_state.copy()

        self.teleports = teleport_borders

        self.neighbours_shifts = self.create_shifts_set(neighbourhood_matrix)

        self.underpopulation_threshold = underpopulation_threshold
        self.overpopulation_threshold = overpopulation_threshold
        self.reproduction_range = reproduction_range

        if plot:
            self.plotting_engine = pe.PlottingEngine(self.size, **kwargs)
            self.plotting_engine.prepare(self.neighbours_shifts, self._portals)
        else:
            self.plotting_engine = None

        self.tends_to_stable = False
        self.is_oscillator = False

    @property
    def size(self) -> Tuple[int, int]:
        return self.height, self.width

    @size.setter
    def size(self, set_val: Union[Tuple[int, int], int]):
        if isinstance(set_val, int):
            self.height, self.width = set_val, set_val
        elif isinstance(set_val, tuple):
            self.height, self.width = set_val

    @property
    def teleports(self):
        return self._portals

    @teleports.setter
    def teleports(self, set_val: Iterable[Union[str, int]]):
        self._portals = set()
        for val in set_val:
            if val in GameOfLife.borders_numbers:
                self._portals.add(val)
            elif str(val).lower().strip() in GameOfLife.borders_names:
                self._portals.add(GameOfLife.borders_name_number_mapping[val.lower().strip()])

    @property
    def reproduction_range(self):
        return self._reproduction_low, self._reproduction_high

    @reproduction_range.setter
    def reproduction_range(self, set_val: Union[Tuple[int, int], int]):
        if isinstance(set_val, int):
            self._reproduction_low, self._reproduction_high = set_val, set_val
        else:
            self._reproduction_low, self._reproduction_high = set_val

    @property
    def living(self):
        return {c for c in self.cells if c.state == 'alive'}

    @property
    def dead(self):
        return {c for c in self.cells if c.state == 'dead'}

    def create_shifts_set(
            self, neighbourhood_matrix: Union[np.ndarray, Iterable[Iterable[int]]]
    ) -> Set[Tuple[int, int]]:
        if neighbourhood_matrix is None:
            neighbourhood_matrix = np.array([
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ])
        elif not isinstance(neighbourhood_matrix, np.ndarray):
            neighbourhood_matrix = np.array(neighbourhood_matrix)
        n_height, n_width = neighbourhood_matrix.shape
        if n_height > self.height or n_width > self.width:
            LOGGER.error('Neighbourhood specified is too big for this game board.')
            raise ValueError('Wrong specification of neighbourhood.')
        if n_height % 2 != 1 or n_width % 2 != 1:
            LOGGER.error('Neighbourhood specified doesnt have odd dimensions.')
            raise ValueError('Wrong specification of neighbourhood.')
        neighbourhood_matrix[n_height // 2, n_width // 2] = 0
        return {
            (-n_width // 2 + 1 + i, n_height // 2 - j)
            for i in range(0, n_width)
            for j in range(0, n_height)
            if neighbourhood_matrix[j, i] == 1
        }

    def link_cells(self):
        for c in self.cells:
            self._link_cell(c)

    def _link_cell(self, c: cell.Cell):
        cell_x, cell_y = c.position
        possible_neighbours_positions = {
            (cell_x + x_offset, cell_y + y_offset) for x_offset, y_offset in self.neighbours_shifts
        }
        linked_positions = {
            (x % self.width, y % self.height)
            for x, y in possible_neighbours_positions
            if self.__is_viable(x, y)
        }
        c.add_neighbours({n_cell for n_cell in self.cells if n_cell.position in linked_positions})

    def __is_viable(self, x: int, y: int):
        if x < 0 and 3 not in self._portals:
            return False
        if x > self.width - 1 and 4 not in self._portals:
            return False
        if y < 0 and 1 not in self._portals:
            return False
        if y > self.height - 1 and 2 not in self._portals:
            return False
        return True

    def process(self, max_iterations: int = 1000):
        for it in range(max_iterations):
            self._process_plotting_machine()
            next_state = self._create_next_state()
            if next_state == self.game_state:
                self.tends_to_stable = True
                if next_state != self.initial_state:
                    self.plotting_engine.loop_n_last_pictures(1, min(20, max_iterations - it))
                break
            if next_state == self.initial_state:
                self.is_oscillator = True
                break
            for c, s in next_state.items():
                c.state = s
            self.game_state = next_state

    def _process_plotting_machine(self):
        if self.plotting_engine is not None:
            self.plotting_engine.draw_alive(self.living)
            self.plotting_engine.draw_dead(self.dead)
            self.plotting_engine.save()

    def _create_next_state(self) -> Dict[cell.Cell, str]:
        next_states = {}
        for c in self.cells:
            neighbours_report = c.report_neighbours_state()
            if c.state == 'alive' and (neighbours_report['alive'] < self.underpopulation_threshold or
                                       neighbours_report['alive'] > self.overpopulation_threshold):
                next_states[c] = 'dead'
            elif c.state == 'dead' and self._reproduction_low <= neighbours_report['alive'] <= self._reproduction_high:
                next_states[c] = 'alive'
            else:
                next_states[c] = c.state
        return next_states

    @staticmethod
    def from_csv(
            grid_path: str,
            delimiter: str = ',', truth_marker: Any = '1',
            neighbourhood_path: Optional[str] = None,
            plot: bool = True, borders: Iterable[Union[str, int]] = ()
    ) -> 'GameOfLife':
        with open(grid_path, 'r') as f_handler:
            this_dir = os.path.join(os.path.dirname(f_handler.name), 'Images')
            levels = []
            for line in f_handler:
                levels.append(line.split(delimiter))
        initial_state = np.array(levels)
        _selector = initial_state == str(truth_marker)
        initial_state[_selector] = 1
        initial_state[~_selector] = 0
        if neighbourhood_path:
            with open(neighbourhood_path, 'r') as f_handler:
                levels = []
                for line in f_handler:
                    levels.append(line.split(delimiter))
            neighbourhood = np.array(levels)
            _selector = neighbourhood == str(truth_marker)
            neighbourhood[_selector] = 1
            neighbourhood[~_selector] = 0
        else:
            neighbourhood = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

        initial_state = initial_state.astype(int)
        neighbourhood = neighbourhood.astype(int)

        return GameOfLife(initial_state, neighbourhood, borders, plot=plot, out_directory=this_dir)


if __name__ == '__main__':
    ins = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ])
    nhood = np.array([
        [1, 0, 0],
        [0, 0, 0],
        [1, 0, 1],
        [0, 0, 0],
        [1, 1, 0]
    ])
    gol = GameOfLife(ins, nhood, teleport_borders=[1, 2, 3, 4], plot=True)
    gol.link_cells()
    gol.process()
    gol.plotting_engine.animate()
    print(gol.is_oscillator)
    print(gol.tends_to_stable)
