import os
from typing import List, Tuple

from AgentBasedModeling.helpers.burning import forest_fire_model as ffm
from AgentBasedModeling.common.log import logger

plt = ffm.pe.slp.plt
LOGGER = logger.get_logger(__name__)
LOGGER.setLevel(10)


def find_percolation_probability(
        lattice_size: int, plant_probability: float, monte_carlo_repetitions: int = 100
) -> float:
    times_burned = 0
    for _ in range(monte_carlo_repetitions):
        fire = ffm.ForestFireModel(lattice_size, plant_probability)
        fire.create_cells()
        fire.plant_trees()
        fire.start_fire()
        fire.burn()
        times_burned += int(fire.is_top_hit)
    return times_burned / monte_carlo_repetitions


def create_percolation_plot(
        lattice_sizes: List[int], probs: List[float], fig_size: Tuple[float, float],
        out_file: str = 'perc_prob.png', monte_carlo_repetitions: int = 100
):
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot()
    line_handlers = []
    for L in lattice_sizes:
        percolation_probs = []
        for p in probs:
            LOGGER.debug(f"Calculating for L = {L}, p = {p}.")
            percolation_probs.append(find_percolation_probability(L, p, monte_carlo_repetitions))
        line_handlers.append(ax.plot(probs, percolation_probs, label=f"L = {L}"))
    ax.legend()
    ax.set_title('Percolation probability for different lattice size.')
    ax.set_xlabel('plant probability')
    ax.set_ylabel('percolation probability')
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
    sizes_to_create = [10, 20, 50, 100]
    probabilities = [p / 10 for p in range(1, 10)]
    create_percolation_plot(sizes_to_create, probabilities, (10, 8), monte_carlo_repetitions=100)


if __name__ == "__main__":
    initialize_all()
