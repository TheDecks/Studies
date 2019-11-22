import os
from typing import Collection

from AgentBasedModeling.helpers.schellings import schellings_model as sm
from AgentBasedModeling.common.log import logger

import matplotlib.pyplot as plt

LOGGER = logger.get_logger(__name__)
LOGGER.setLevel('DEBUG')


def save_figure_to_file(fig, file: str):
    file_name, file_format = file.split('.')
    out_file_template = f"{file_name}_{{}}.{file_format}"
    counter = 0
    while os.path.exists(file):
        counter += 1
        file = out_file_template.format(counter)
    fig.savefig(file)


def create_initial_and_final_pictures_only(
        grid_length: int = 100,
        neighbourhood_depth: int = 1,
        agents_counts: Collection[int] = (250, 250),
        thresholds: Collection[int] = (4, 4),
        movement_type: str = 'random',
        good_enough_threshold: int = -1,
        max_check_places: int = 10
):
    sch_model = sm.SchellingModel(grid_length, neighbourhood_depth, agents_counts,thresholds, plot=True)
    sch_model.create_cells_links()
    sch_model.process_plotting()
    sch_model.simulate(
        movement_type=movement_type,
        good_enough_threshold=good_enough_threshold,
        max_check_places=max_check_places
    )
    sch_model.process_plotting()


def iterations_to_population_size_relation(
        population_sizes: Collection[Collection[int]],
        file: str,
        grid_length: int = 100,
        neighbourhood_depth: int = 1,
        thresholds: Collection[int] = (4, 4),
        movement_type: str = 'random',
        good_enough_threshold: int = -1,
        max_check_places: int = 10
):
    no_iterations = []
    for agents_counts in population_sizes:
        LOGGER.debug(f'Processing for agents count: {agents_counts}.')
        sch_model = sm.SchellingModel(grid_length, neighbourhood_depth, agents_counts, thresholds, plot=False)
        sch_model.create_cells_links()
        ret_dict = sch_model.simulate(
            movement_type=movement_type,
            good_enough_threshold=good_enough_threshold,
            max_check_places=max_check_places
        )
        for _, sni_list in ret_dict.items():
            no_iterations.append(len(sni_list))
            break

    fig = plt.figure(figsize=(5, 7))
    ax = fig.add_subplot()
    ax.plot([sum(sizes) for sizes in population_sizes], no_iterations)
    ax.set_xlabel('Population size summed')
    ax.set_ylabel('Iterations performed')
    ax.set_title(f'{movement_type} moving type, {neighbourhood_depth} neighbourhood_depth')
    save_figure_to_file(fig, file)


def segregation_index_to_acceptance_relation(
        thresholds_to_check: Collection[Collection[int]],
        file: str,
        grid_length: int = 100,
        neighbourhood_depth: int = 1,
        agents_counts: Collection[int] = (2500, 2500),
        movement_type: str = 'random',
        good_enough_threshold: int = -1,
        max_check_places: int = 10
):
    sni_dict = {i: [] for i in range(len(agents_counts))}
    for thresholds in thresholds_to_check:
        LOGGER.debug(f'Processing for thresholds {thresholds}.')
        sch_model = sm.SchellingModel(grid_length, neighbourhood_depth, agents_counts, thresholds, plot=False)
        sch_model.create_cells_links()
        sch_model.simulate(
            movement_type=movement_type,
            good_enough_threshold=good_enough_threshold,
            max_check_places=max_check_places
        )
        for agent_type, sni in sch_model.get_sni().items():
            sni_dict[agent_type].append(sni)

    fig = plt.figure(figsize=(5, 7))
    ax = fig.add_subplot()
    colors = sm.plt_engine.PlottingEngine.get_colours_sequence(len(agents_counts))
    lines = []
    for agent_type, sni_vals in sni_dict.items():
        lines.append(ax.plot(
            [th[agent_type] for th in thresholds_to_check],
            sni_vals, color=colors[agent_type],
            label=f'Declaration pos. {agent_type}'
        ))
    ax.set_xlabel('Happiness threshold')
    ax.set_ylabel('Similar neighbour index')
    ax.legend()
    ax.set_title(f'{movement_type} moving type, {neighbourhood_depth} neighbourhood_depth')
    save_figure_to_file(fig, file)


def segregation_index_to_neighbourhood_relation(
        depths: Collection[int],
        file: str,
        grid_length: int = 100,
        agents_counts: Collection[int] = (2500, 2500),
        movement_type: str = 'random',
        good_enough_threshold: int = -1,
        max_check_places: int = 10
):
    sni_dict = {i: [] for i in range(len(agents_counts))}
    for neighbourhood_depth in depths:
        LOGGER.debug(f'Processing for depth {neighbourhood_depth}.')
        sch_model = sm.SchellingModel(
            grid_length,
            neighbourhood_depth,
            agents_counts,
            tuple([((neighbourhood_depth * 2 + 1)**2 - 1)/2 for _ in range(len(agents_counts))]),
            plot=False
        )
        sch_model.create_cells_links()
        sch_model.simulate(
            movement_type=movement_type,
            good_enough_threshold=good_enough_threshold,
            max_check_places=max_check_places
        )
        for agent_type, sni in sch_model.get_sni().items():
            sni_dict[agent_type].append(sni)

    fig = plt.figure(figsize=(5, 7))
    ax = fig.add_subplot()
    colors = sm.plt_engine.PlottingEngine.get_colours_sequence(len(agents_counts))
    lines = []
    for agent_type, sni_vals in sni_dict.items():
        lines.append(ax.plot(
            depths,
            sni_vals, color=colors[agent_type],
            label=f'Declaration pos. {agent_type}'
        ))
    ax.set_xlabel('Happiness threshold')
    ax.set_ylabel('Similar neighbour index')
    ax.legend()
    ax.set_title(f'{movement_type} moving type')
    save_figure_to_file(fig, file)


if __name__ == '__main__':
    iterations_to_population_size_relation(
        [(p_size, p_size) for p_size in range(250, 4050, 50)],
        'iter_to_pop_250_4000_random_5000_agents.png'
    )

    segregation_index_to_acceptance_relation(
        [(th, th) for th in range(1, 8)],
        'sni_to_th_1_7_random_5000_agents.png'
    )
    segregation_index_to_neighbourhood_relation(
        range(1, 6),
        'sni_to_d_1_5_random_5000_agents.png'
    )

    ###

    iterations_to_population_size_relation(
        [(p_size, p_size) for p_size in range(250, 4050, 50)],
        'iter_to_pop_250_4000_happy_5000_agents.png',
        movement_type='happy'
    )

    segregation_index_to_neighbourhood_relation(
        range(1, 6),
        'sni_to_d_1_5_happy_5000_agents.png',
        movement_type='happy'
    )

    segregation_index_to_acceptance_relation(
        [(th, th) for th in range(1, 8)],
        'sni_to_th_1_7_happy_5000_agents.png',
        movement_type='happy'
    )
