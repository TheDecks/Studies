from typing import Dict

from AnalysisOfUnstructuredData import ROOT_PATH
from AnalysisOfUnstructuredData.helpers.titanic import namespaces as ns
from AnalysisOfUnstructuredData.common.log import logger
import pandas as pd
import os


class DataManager:

    def __init__(self, file_name: str = 'titanic.csv'):
        self.file_path = os.path.join(ROOT_PATH, 'data_sources', 'list1', file_name)
        self.nm = ns.TrainSetNamespaceManager
        self.data = pd.DataFrame()

    def load_data_into_df(self):
        self.data = pd.read_csv(self.file_path)
        self.data = self.data.rename(columns=self.nm.mapping)

    def remove_casing(self):
        self.data = self.data.apply(
            lambda col: col.str.casefold() if self.nm.expected_data_types[col.name] == str else col
        )

    def find_mismatching_values(self):
        return {
            col_name: set(self.data[col_name]) - possible_values
            for col_name, possible_values in self.nm.accepted_values.items()
        }

    def check_types(self):
        self.data = self.data.apply(
            lambda col: col.apply(
                lambda x: self.nm.expected_data_types[col](x) if x != pd.np.nan else x
            )
        )

    def report_missing(self) -> Dict[str, int]:
        def missing_vals_by_column(col):
            return col.name, col.isnull().sum()
        return dict(self.data.apply(lambda col: missing_vals_by_column(col)).values)
