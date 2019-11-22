import os
from typing import List, Tuple

from AgentBasedModeling.helpers.burning import forest_fire_model as ffm
from AgentBasedModeling.common.log import logger

plt = ffm.pe.slp.plt

LOGGER = logger.get_logger(__name__)
LOGGER.setLevel(10)


def find_avg_cluster(
    lattice_size: int, plant_probability: float, state: str = 'burned', monte_carlo_repetitions: int = 100
):
    summed_cluster_sizes = 0
    for _ in range(monte_carlo_repetitions):
        fire = ffm.ForestFireModel(lattice_size, plant_probability)
        fire.create_cells()
        fire.plant_trees()
        fire.start_fire()
        fire.burn()
        summed_cluster_sizes += fire.find_biggest_cluster_by_me(state)

    return summed_cluster_sizes / monte_carlo_repetitions


def create_cluster_plot(
    lattice_size: int, probs: List[float], fig_size: Tuple[float, float], state: str = 'burned',
    out_file: str = 'cluster_size.png', monte_carlo_repetitions: int = 100
):
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot()
    line_handlers = []
    cluster_sizes = []
    for p in probs:
        LOGGER.debug(f"Calculating for p = {p}.")
        cluster_sizes.append(find_avg_cluster(lattice_size, p, state, monte_carlo_repetitions))
    line_handlers.append(ax.plot(probs, cluster_sizes, label=f"L = {lattice_size}"))
    ax.legend()
    ax.set_title('Average biggest cluster size.')

    ax.set_xlabel('plant probability')
    ax.set_ylabel('cluster size')
    file_name, file_format = out_file.split('.')
    out_file_template = f"{file_name}_{{}}.{file_format}"
    counter = 0
    while os.path.exists(out_file):
        counter += 1
        out_file = out_file_template.format(counter)
    fig.savefig(out_file)


def initialize_all(wind_angle: float = 0, wind_power: float = 0, wind_random: bool = False):
    ffm.wind.Wind().power = wind_power
    ffm.wind.Wind().direction = wind_angle
    ffm.wind.Wind().is_state_random = wind_random
    probabilities = [p / 30 for p in range(1, 30)]
    create_cluster_plot(100, probabilities, (10, 8), monte_carlo_repetitions=100)


if __name__ == '__main__':
    initialize_all()
