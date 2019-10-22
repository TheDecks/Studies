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
