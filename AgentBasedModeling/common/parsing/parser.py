import argparse
import os


class ProjectArgParser(argparse.ArgumentParser):

    def __init__(self, **kwargs):
        super().__init__(description='Agent Based Modelling', **kwargs)
        self._subs = self.add_subparsers(dest='list')

    def create_common(self):
        self.add_argument(
            '--out_path', '-o',
            action='store', type=str, required=False, default=os.path.join('AgentBasedModeling', 'Results'),
            help='Either output directory or file.'
        )

    def create_list_subparsers(self):
        self._list_subparser_1()
        self._list_subparser_3()
        self._list_subparser_4()

    def _list_subparser_1(self):

        l_par = self._subs.add_parser('one', help='Options for list 1.')
        l_par.set_defaults(list='one')

        l_par.add_argument(
            '--wind_direction', '-d',
            action='store', required=False, default=0, type=float,
            help='Specify wind direction.'
        )

        l_par.add_argument(
            '--wind_strength', '-s',
            action='store', required=False, default=0, type=float,
            help='Specify wind power.'
        )

        l_par.add_argument(
            '--wind_random', '-r',
            action='store_true', required=False,
            help='Specify if wind should change each step.'
        )

        l_par.add_argument(
            '--lattice_size', '-l',
            action='store', required=True, type=int,
            help='Grid side length.'
        )

        l_par.add_argument(
            '--plant_probability', '-p',
            action='store', required=True, type=float,
            help='Tree planting probability.'
        )

        l_par.add_argument(
            '--draw_results',
            action='store_true', required=False,
            help='Animation will be created.'
        )

    def _list_subparser_3(self):
        l_par = self._subs.add_parser('three', help='Options for list 3.')
        l_par.set_defaults(list='three')

        l_par.add_argument(
            '--initial_state_file', '-i',
            action='store', required=True,
            help='Path to file with initial state of game.'
        )

        l_par.add_argument(
            '--neighbourhood_file', '-n',
            action='store', required=False,
            help='Path to file with neighbourhood definition.'
        )

        l_par.add_argument(
            '--pass_through_border', '-b',
            action='append', required=False,
            choices=['bottom', 'top', 'left', 'right'],
            default=[], dest='borders',
            help='Aggregate borders that are passable.'
        )

        l_par.add_argument(
            '--up_threshold',
            action='store', required=False, type=int, default=2,
            help='Underpopulation threshold. Cell having less than this number of alive neighbours dies.'
        )

        l_par.add_argument(
            '--op_threshold',
            action='store', required=False, type=int, default=3,
            help='Overpopulation threshold. Cell having more than this number of alive neighbours dies.'
        )

        l_par.add_argument(
            '--reproduction_range',
            action='store', required=False, nargs=2, type=int, default=[3, 3],
            help='Range of number of alive cells that a dead cell must have to be brought to life.'
        )

        l_par.add_argument(
            '--separator', '-s',
            action='store', required=False, default=',',
            help='Input files delimiters.'
        )

        l_par.add_argument(
            '--alive_marker', '-m',
            action='store', required=False, default='1',
            help='Marker used to denote alive cell in input file. Same marker of neighbouring must be used.'
        )

    def _list_subparser_4(self):
        l_par = self._subs.add_parser('four', help='Options for list 4.')
        l_par.set_defaults(list='four')

        l_par.add_argument(
            '--grid_length', '-l',
            action='store', required=False, default=100, type=int,
            help='Length of grid.'
        )

        l_par.add_argument(
            '--neighbourhood_depth', '-d',
            action='store', required=False, default=1, type=int,
            help="Moore's neighbourhood number of levels."
        )

        l_par.add_argument(
            '--agents_count', '-c',
            action='store', nargs='*', required=False, default=[2500, 2500], type=int,
            help="Each group's number of agent."
        )

        l_par.add_argument(
            '--happiness_thresholds', '-t',
            action='store', nargs='*', required=False, default=[4, 4], type=int,
            help="Eeach group's number of similar neighbours to be happy."
        )

        l_par.add_argument(
            '--plot',
            action='store_true', required=False,
            help='Whether to create an animation.'
        )

        l_par.add_argument(
            '--max_iter',
            action='store', required=False, default=10000, type=int,
            help='Maximal number of iterations to perform.'
        )

        l_par.add_argument(
            '--movement_type',
            action='store', required=False, default='random', type=str,
            choices=['random', 'happiness'],
            help='Type of moving to perform on unhappy agents.'
        )