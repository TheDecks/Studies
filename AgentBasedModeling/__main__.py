from typing import Callable

from AgentBasedModeling.common.log import logger, logger_dec as ld
import AgentBasedModeling.common.parsing.parser as parser

LOGGER = logger.get_logger(__name__)
LOGGER.setLevel('DEBUG')


class MainInterface:

    _arg_parser: parser.ProjectArgParser

    def __init__(self):
        self._arg_parser = parser.ProjectArgParser()
        self.initialize_parser()
        self._args = self._arg_parser.parse_args()

    def run(self):
        list_run_method = self._list_choosing_factory()
        list_run_method()

    def initialize_parser(self):
        self._arg_parser.create_common()
        self._arg_parser.create_list_subparsers()

    def _list_choosing_factory(self) -> Callable:
        if self._args.list == 'one':
            return self.__run_list_1
        elif self._args.list == 'three':
            return self.__run_list_3
        elif self._args.list == 'four':
            return self.__run_list_4

    @ld.debug_timer_dec(logger=LOGGER)
    def __run_list_1(self):
        from AgentBasedModeling.helpers.burning import wind, forest_fire_model as ffm
        wind.Wind(self._args.wind_direction, self._args.wind_strength, self._args.wind_random)
        if self._args.draw_results:
            plt_eng = ffm.pe.PlottingEngine(self._args.lattice_size, (11.5, 8), out_directory=self._args.out_path)
        else:
            plt_eng = None
        fire = ffm.ForestFireModel(self._args.lattice_size, self._args.plant_probability, plt_eng)
        fire.create_cells()
        fire.plant_trees()
        fire.start_fire()
        fire.burn()
        if fire.is_top_hit:
            LOGGER.info('List 1, fire reached the other side of forest.')
        else:
            LOGGER.info('List 1, fire did not reach the other side of forest.')
        LOGGER.info('Biggest cluster of burned trees amounts {n} trees'.format(n=fire.find_biggest_cluster_by_me()))

    @ld.debug_timer_dec(logger=LOGGER)
    def __run_list_3(self):
        from AgentBasedModeling.helpers.game_of_life.game import GameOfLife
        gol = GameOfLife.from_csv(
            self._args.initial_state_file,
            delimiter=self._args.separator,
            truth_marker=self._args.alive_marker,
            neighbourhood_path=self._args.neighbourhood_file,
            borders=self._args.borders
        )

        gol.overpopulation_threshold = self._args.op_threshold
        gol.underpopulation_threshold = self._args.up_threshold
        gol.reproduction_range = self._args.reproduction_range
        gol.link_cells()
        gol.process()
        gol.plotting_engine.animate()

    @ld.debug_timer_dec(logger=LOGGER)
    def __run_list_4(self):
        import AgentBasedModeling.helpers.schellings.schellings_model as sm
        import matplotlib.pyplot as plt
        import os
        if len(self._args.happiness_thresholds) == 1:
            thresholds = self._args.happiness_thresholds[0]
        else:
            thresholds = self._args.happiness_thresholds
        s_m = sm.SchellingModel(
            self._args.grid_length,
            self._args.neighbourhood_depth,
            self._args.agents_count,
            thresholds,
            plot=self._args.plot,
            out_directory=self._args.out_path
        )
        s_m.create_cells_links()
        res = s_m.simulate(1, self._args.movement_type, max_iter=self._args.max_iter)
        fig = plt.figure(figsize=(5, 7))
        ax = fig.add_subplot()
        colors = sm.plt_engine.PlottingEngine.get_colours_sequence(3)
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
        plt.show()
        # file = os.path.join(self._args.out_directory, 'time_evolution_three_groups.png')
        # file_name, file_format = file.split('.')
        # out_file_template = f"{file_name}_{{}}.{file_format}"
        # counter = 0
        # while os.path.exists(file):
        #     counter += 1
        #     file = out_file_template.format(counter)
        # fig.savefig(file)


if __name__ == "__main__":
    MainInterface().run()
