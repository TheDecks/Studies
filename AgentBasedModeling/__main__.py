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
        print(self._args)
        if self._args.list == 'one':
            return self.__run_list_1

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


if __name__ == "__main__":
    MainInterface().run()
