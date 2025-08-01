import os
from logger_n_exception.logger import logging
import pandas as pd
import numpy as np

DATASET_PATH = 'task_logs/tasks_data.csv'

class DataFrameManager():
    def __init__(self, file_path=DATASET_PATH):
        self.file_path = file_path
        self.df = self.load_dataframe()
        logging.info(f"DataFrame loaded from {self.file_path}")

    def __repr__(self):
        return f"DataFrameManager(file_path={self.file_path})"
    
    def __str__(self):
        return f"DataFrameManager managing DataFrame with {len(self.df)} rows and {len(self.df.columns)} columns."

    def load_dataframe(self):
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path)
        else:
            logging.error(f"File {self.file_path} does not exist. Returning empty DataFrame.")
            return pd.DataFrame()

    def save_dataframe(self):
        self.df.to_csv(self.file_path, index=False)
        logging.info(f'DataFrame saved to {self.file_path}')

    def get_dataframe(self):
        return self.df

    def update_dataframe(self, new_data):
        if isinstance(new_data, pd.DataFrame):
            self.df = pd.concat([self.df, new_data], ignore_index=True)
            self.df.drop_duplicates(inplace=True)
            logging.info(f"DataFrame updated with new data. Current size: {len(self.df)} rows.")
        else:
            raise ValueError("New data must be a pandas DataFrame")
        self.save_dataframe()