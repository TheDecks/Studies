import re
from typing import List, Union

from AnalysisOfUnstructuredData.common.log import logger
from AnalysisOfUnstructuredData.lists.list1 import data_preprocessor as dp
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.text as text

nm = dp.ns.TrainSetNamespaceManager
LOGGER = logger.get_logger(__name__)


class TitanicAnalyser:

    def __init__(self):
        self.nm = dp.ns.TrainSetNamespaceManager
        self.data_manager = dp.DataManager('titanic.csv')

    def preprocess_data(self):
        self.data_manager.load_data_into_df()
        self.data_manager.remove_casing()

    def log_data_report(self):
        missing_vals = self.data_manager.report_missing()
        mismatch_vals = self.data_manager.find_mismatching_values()

        LOGGER.info('Mismatching values in factorial columns report: \n\t\t{}'.format(
            '\n\t\t'.join([k + ': ' + str(v) for k, v in mismatch_vals.items()])
        ))

        LOGGER.info('Missing values counter report: \n\t\t{}'.format(
            '\n\t\t'.join([k + ': ' + str(v) for k, v in missing_vals.items()])
        ))

        LOGGER.info('{col_name} contains too many missing values.'.format(col_name=nm.df_cabin_no_col))
        LOGGER.info('No absurd values found in factorial columns.')
        LOGGER.info('{col_name} column could be later filled.'.format(col_name=nm.df_age_col))

    def create_pie_chart(self, by: Union[str, List[str], None] = None):
        if by is None:
            by = [self.nm.df_sex_col]
        elif isinstance(by, str):
            by = [by]
        this_data = self.data_manager.data[by].copy()
        this_data['Percentage'] = 1
        ax = this_data.groupby(by=by).agg('sum').plot.pie(
            y='Percentage', legend=False, autopct='%1.1f%%'
        )
        ax.set_ylabel('')
        for child in ax.get_children():
            if isinstance(child, text.Text):
                if re.search('^[(].*[)]$', child.get_text()):
                    new_text = child.get_text()
                    for old, new in {', 0': ', No', ', 1': ', Yes', '(': '', ')': ''}.items():
                        new_text = new_text.replace(old, new)
                    child.set_text(new_text)
        ax.figure.suptitle(', '.join(by))
        return ax.figure, ax

    def create_scatter_plot(self, what: str, in_relation_to: str, by: Union[str, List[str], None] = None):
        if isinstance(by, str):
            by = [by]
        fig = plt.figure()
        ax = fig.add_subplot()
        if by is not None:
            grouper = self.data_manager.data.groupby(by=by)
            colour_map = cm.get_cmap('rainbow', len(grouper))
            col_iter = 0
            for label, df in grouper:
                if isinstance(label, tuple):
                    new_label = ', '.join(map(str, label))
                    for old, new in {', 0': ', No', ', 1': ', Yes', '(': '', ')': ''}.items():
                        new_label = new_label.replace(old, new)
                else:
                    new_label = label
                df.plot.scatter(x=in_relation_to, y=what, ax=ax, label=new_label, c=[colour_map(col_iter)])
                col_iter += 1
        else:
            self.data_manager.data.plot.scatter(x=in_relation_to, y=what, ax=ax)
        ax.figure.suptitle(', '.join(by))
        return fig, ax

    @property
    def survived(self):
        return sum(self.data_manager.data[self.nm.df_survive_col] == 1)

    def create_histogram(self, by: str = 'FareFee'):
        ax = self.data_manager.data[by].plot.hist(bins=30)
        ax.figure.suptitle(by)
        return ax.figure, ax
