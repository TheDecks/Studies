import os
from typing import Callable

from AnalysisOfUnstructuredData.common.log import logger, logger_dec as ld
import AnalysisOfUnstructuredData.common.parsing.parser as parser

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

    @ld.debug_timer_dec(logger=LOGGER)
    def __run_list_1(self):
        from AnalysisOfUnstructuredData.lists.list1 import analysis as a
        analyser = a.TitanicAnalyser()
        analyser.preprocess_data()
        if self._args.report:
            analyser.log_data_report()
        if self._args.survived:
            LOGGER.info("{} people survived.".format(analyser.survived))
        if self._args.plot_type is not None:
            by = list(map(a.nm.try_retrieve_mapping, self._args.by))
            if self._args.plot_type == 'pie':
                fig, _ = analyser.create_pie_chart(by)
            elif self._args.plot_type == 'scatter':
                y = a.nm.try_retrieve_mapping(self._args.y)
                x = a.nm.try_retrieve_mapping(self._args.x)
                fig, _ = analyser.create_scatter_plot(y, x, by=by)
            else:
                fig, _ = analyser.create_histogram(by[0])
            if self._args.fig_size is not None:
                fig.set_size_inches(tuple(self._args.fig_size))
            out_file_template = os.path.join(self._args.out_path, '{}.png')
            counter = 1
            out_file = out_file_template.format(counter)
            while os.path.exists(out_file):
                counter += 1
                out_file = out_file_template.format(counter)
            fig.savefig(out_file)


if __name__ == "__main__":
    MainInterface().run()
