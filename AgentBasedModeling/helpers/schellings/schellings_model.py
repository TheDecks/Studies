from typing import Set, Union, Optional, Collection, Dict, Tuple, List
from AgentBasedModeling.helpers.schellings import cell, plt_engine
import random


class SchellingModel:

    _thresholds: Collection[int]
    _agent_names: Collection[Union[int, str]]
    plotting_engine: Optional[plt_engine.PlottingEngine]
    name_to_threshold: Dict[Union[str, int, None], int]
    empties: Set[cell.Cell]
    occupied: Set[cell.Cell]

    def __init__(
            self,
            grid_length: int,
            neighbourhood_depth: int,
            agents_counts: Collection[int],
            agents_happiness_thresholds: Union[int, Collection[int]],
            agents_names: Optional[Collection[Union[str, int]]] = None,
            plot: bool = False,
            **kwargs
    ):
        self.grid_length = grid_length
        self.neighbourhood_depth = neighbourhood_depth
        self.types_count = len(agents_counts)
        self.thresholds = agents_happiness_thresholds
        self.agent_names = agents_names
        self.name_to_threshold = {name: th for name, th in zip(self.agent_names, self.thresholds)}
        _temp_cells = {cell.Cell(x, y) for x in range(self.grid_length) for y in range(self.grid_length)}
        _temp_agents = [self.agent_names[i] for i in range(self.types_count) for _ in range(agents_counts[i])]
        self.occupied = set(random.sample(_temp_cells, sum(agents_counts)))
        self.empties = _temp_cells - self.occupied
        for i, c in enumerate(self.occupied):
            c.agent = _temp_agents[i]
        if plot:
            self.plotting_engine = plt_engine.PlottingEngine(self.grid_length, groups_count=self.types_count, **kwargs)
            self.plotting_engine.prepare(self.thresholds, (self.neighbourhood_depth * 2 + 1) ** 2 - 1)
        else:
            self.plotting_engine = None

    @property
    def thresholds(self) -> Collection[int]:
        return self._thresholds

    @thresholds.setter
    def thresholds(self, set_val: Union[int, Collection[int]]):
        if isinstance(set_val, int):
            self._thresholds = [set_val for _ in range(self.types_count)]
        else:
            self._thresholds = [th for th in set_val]

    @property
    def agent_names(self) -> Collection[Union[int, str]]:
        return self._agent_names

    @agent_names.setter
    def agent_names(self, set_val: Optional[Collection[Union[str, int]]]):
        if set_val is None:
            self._agent_names = [i for i in range(self.types_count)]
        else:
            self._agent_names = [name for name in set_val]

    def create_cells_links(self):
        shifts = {
            (x, y)
            for x in range(-self.neighbourhood_depth, self.neighbourhood_depth + 1)
            for y in range(-self.neighbourhood_depth, self.neighbourhood_depth + 1)
        }
        shifts.remove((0, 0))
        for c in self.empties | self.occupied:
            self._link_cell(c, shifts)

    def _link_cell(self, c: cell.Cell, shifts: Collection[Tuple[int, int]]):
        c_x, c_y = c.position
        to_link_positions = {
            ((c_x + x_off) % self.grid_length, (c_y + y_off) % self.grid_length)
            for x_off, y_off in shifts
        }
        c.add_neighbours({n_cell for n_cell in self.empties | self.occupied if n_cell.position in to_link_positions})

    def is_everyone_happy(self) -> bool:
        for c in self.occupied:
            if not c.is_agent_happy(self.name_to_threshold[c.agent]):
                return False
        return True

    def get_occupied_split(self) -> Collection[Collection['cell.Cell']]:
        _d = {agent_type: [] for agent_type in self.agent_names}
        for agent in self.occupied:
            _d[agent.agent].append(agent)
        return [_d[agent_type] for agent_type in self.agent_names]

    def process_plotting(self):
        if self.plotting_engine is not None:
            self.plotting_engine.draw_empties(self.empties)
            self.plotting_engine.draw_groups(self.get_occupied_split())
            self.plotting_engine.save()

    def get_sni(self) -> Dict[str, float]:
        _d = {agent_type: [] for agent_type in self.agent_names}
        for agent in self.occupied:
            _d[agent.agent].append(agent.segregation_index())
        return {agent_type: sum(indices) / len(indices) for agent_type, indices in _d.items()}

    def simulate(
            self,
            process_others_step: Optional[int] = None,
            movement_type: str = 'random',
            good_enough_threshold: int = -1,
            max_check_places: int = 10,
            max_iter: int = 10000
    ) -> Dict[str, List[Optional[float]]]:
        save_step = max_iter + 1 if process_others_step is None else process_others_step
        sni = {agent_type: [] for agent_type in self.agent_names}
        for step_no in range(max_iter):
            if (step_no + 1) % save_step == 0:
                self.process_plotting()
                current_sni = self.get_sni()
                for agent_type, index in current_sni.items():
                    sni[agent_type].append(index)
            else:
                for agent_type in sni.keys():
                    sni[agent_type].append(None)
            if self.is_everyone_happy():
                break
            to_be_processed = self.occupied.copy()
            how_many_moved = 0
            while to_be_processed:
                moved = False
                agent = to_be_processed.pop()
                if not agent.is_agent_happy(self.name_to_threshold[agent.agent]):
                    if movement_type == 'random':
                        moved = self.move_agent_random(agent)
                    elif movement_type == 'happy':
                        moved = self.move_agent_happy(agent, max_check_places)
                how_many_moved += int(moved)
            if how_many_moved <= good_enough_threshold:
                break

        return sni

    def move_agent_random(self, agent: cell.Cell) -> bool:
        move_to_place = self.empties.pop()
        move_to_place.agent = agent.agent
        self.occupied.add(move_to_place)
        agent.agent = None
        self.occupied.remove(agent)
        self.empties.add(agent)
        return True

    def move_agent_happy(self, agent: cell.Cell, max_check_places: int) -> bool:
        possible_places = random.sample(self.empties, max_check_places)
        for move_to_place in possible_places:
            if move_to_place.would_be_happy(agent.agent, self.name_to_threshold[agent.agent]):
                move_to_place.agent = agent.agent
                agent.agent = None
                self.occupied.add(move_to_place)
                self.occupied.remove(agent)
                self.empties.add(agent)
                self.empties.remove(move_to_place)
                return True
        return False


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import os
    # sm = SchellingModel(100, 1, [250, 250], [4, 4], plot=True)
    # sm.create_cells_links()
    # sm.process_plotting()
    # sm.simulate(movement_type='random')
    # sm.process_plotting()
    sm = SchellingModel(100, 1, [2500, 2500, 2500], [3, 4, 5], plot=True)
    sm.create_cells_links()
    res = sm.simulate(1, movement_type='random', max_iter=500)
    # sm.plotting_engine.animate()
    fig = plt.figure(figsize=(5, 7))
    ax = fig.add_subplot()
    colors = plt_engine.PlottingEngine.get_colours_sequence(3)
    lines = []
    for agent_type, sni_vals in res.items():
        lines.append(ax.plot(
            range(1, len(sni_vals) + 1),
            sni_vals, color=colors[agent_type],
            label=f'Declaration pos. {agent_type}'
        ))
    ax.set_xlabel('iteration step')
    ax.set_ylabel('Similar neighbour index')
    ax.legend()
    file = 'time_evolution_three_groups.png'
    file_name, file_format = file.split('.')
    out_file_template = f"{file_name}_{{}}.{file_format}"
    counter = 0
    while os.path.exists(file):
        counter += 1
        file = out_file_template.format(counter)
    fig.savefig(file)
