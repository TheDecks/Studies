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
