import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

from domain.models import Experiment
from infrastructure.repositories import ExperimentRepository


class ImportService:
    def __init__(self):
        self.experiment_repo = ExperimentRepository()

    def import_from_csv(self, file_path: str, article_id: int = 1) -> Experiment:
        path = Path(file_path)
        
        element_names = pd.read_csv(path, nrows=0).columns.to_list()
        parameters = pd.read_csv(path, skiprows=[0]).columns.astype('float').to_list()
        
        temperature = None if np.isnan(parameters[0]) else parameters[0]
        pressure = None if np.isnan(parameters[1]) else parameters[1]
        
        df = pd.read_csv(path, skiprows=range(2))
        source_data = self._dataframe_to_dict(df)
        
        experiment = Experiment(
            first_element=element_names[0],
            second_element=element_names[1],
            temperature=temperature,
            pressure=pressure,
            source_data=source_data,
            article_id=article_id
        )
        
        return experiment

    def import_and_save(self, file_path: str, article_id: int = 1) -> int:
        experiment = self.import_from_csv(file_path, article_id)
        return self.experiment_repo.create(experiment)

    def _dataframe_to_dict(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        result = {}
        for column in df.columns:
            result[column] = df[column].tolist()
        return result