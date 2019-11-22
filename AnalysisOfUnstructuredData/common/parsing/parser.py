import argparse
import os


class ProjectArgParser(argparse.ArgumentParser):

    def __init__(self, **kwargs):
        super().__init__(description='Agent Based Modelling', **kwargs)
        self._subs = self.add_subparsers(dest='list')

    def create_common(self):
        self.add_argument(
            '--out_path', '-o',
            action='store', type=str, required=False, default=os.path.join('AnalysisOfUnstructuredData', 'Results'),
            help='Either output directory or file.'
        )

    def create_list_subparsers(self):
        self._list_subparser_1()
        self._list_subparser_2()
        self._list_subparser_3()

    def _list_subparser_1(self):

        l_par = self._subs.add_parser('one', help='Options for list 1.')
        l_par.set_defaults(list='one')

        l_par.add_argument(
            '--report',
            action='store_true', required=False,
            help='Show report info on data. (As of now, a really dumb one)'
        )

        l_par.add_argument(
            '--survived',
            action='store_true', required=False,
            help='Report number of survivors.'
        )
        l_par.add_argument(
            '--fig_size',
            action='store', nargs=2, required=False,
            help='Specify output plot size.'
        )

        l_par.add_argument(
            '--plot_type', '-p',
            action='store', type=str, required=False, choices=['pie', 'scatter', 'hist'],
            help='Specify plot type.'
        )

        l_par.add_argument(
            '--by',
            action='append', type=str,
            help='Specify by which variables plot will be grouped.'
        )

        l_par.add_argument(
            '-x',
            action='store', type=str, required=False,
            help='X Axis variable. (only for scatter)'
        )
        l_par.add_argument(
            '-y',
            action='store', type=str, required=False,
            help='Y Axis variable. (only for scatter)'
        )

    def _list_subparser_2(self):
        l_par = self._subs.add_parser('two', help='Options for list 2.')
        l_par.set_defaults(list='two')

        l_par.add_argument(
            '--show_non_hsc',
            action='store_true', required=False,
            help='Whether to include people outside of HSC.'
        )

        l_par.add_argument(
            '--person', '-p',
            action='store', nargs=2, required=False, type=str, default=['', ''],
            help='Person to be checked. Signature is -p/--person NAME SURNAME.'
        )

        l_par.add_argument(
            '--section',
            action='append', type=str, dest='sections', default=[],
            help='Specify sections to be parsed.'
        )

    def _list_subparser_3(self):
        l_par = self._subs.add_parser('three', help='Options for list 3.')
        l_par.set_defaults(list='three')

        l_par.add_argument(
            '--city',
            action='store', required=False, default='London',
            help='Specify starting city.'
        )

        l_par.add_argument(
            '--distance',
            action='store', required=False, default=3100, type=float,
            help='Distance threshold for single step length.'
        )

        l_par.add_argument(
            '--final_threshold',
            action='store', required=False, default=300, type=float,
            help='Terminating condition distance. Too low value might result in infinite loop.'
        )

        l_par.add_argument(
            '--occurrences',
            action='store', required=False, default=2, type=int,
            help='Set minimum times a city name must occur to be included.'
        )

        l_par.add_argument(
            '--population',
            action='store', required=False, default=78000, type=int,
            help='Set minimal population of town for it to be considered.'
        )