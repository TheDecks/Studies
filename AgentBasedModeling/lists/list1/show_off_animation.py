from typing import Tuple

from AgentBasedModeling.helpers.burning import forest_fire_model as ffm


def create_animation(
        lattice_size: int, plant_probability: float, out_fig_size: Tuple[float, float] = (11.5, 8),
        wind_angle: float = 0, wind_power: float = 0, wind_random: bool = False
):
    ffm.wind.Wind().power = wind_power
    ffm.wind.Wind().direction = wind_angle
    ffm.wind.Wind().is_state_random = wind_random

    fire = ffm.ForestFireModel(
        lattice_size, plant_probability, ffm.pe.PlottingEngine(lattice_size, out_fig_size, 'Anim_dump_folder')
    )
    fire.create_cells()
    fire.plant_trees()
    fire.start_fire()
    fire.burn()


if __name__ == "__main__":
    create_animation(30, 0.5)
    create_animation(30, 0.5, wind_angle=30, wind_power=0.5, wind_random=False)
    create_animation(30, 0.5, wind_angle=60, wind_power=0.3, wind_random=True)
