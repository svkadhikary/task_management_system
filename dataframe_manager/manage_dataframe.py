import os
import pandas as pd
import numpy as np

DATASET_PATH = 'task_logs/tasks_data.csv'

class DataFrameManager():
    def __init__(self, file_path=DATASET_PATH):
        self.file_path = file_path
        self.df = self.load_dataframe()

    def load_dataframe(self):
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path)
        else:
            return pd.DataFrame()

    def save_dataframe(self):
        self.df.to_csv(self.file_path, index=False)

    def get_dataframe(self):
        return self.df

    def update_dataframe(self, new_data):
        if isinstance(new_data, pd.DataFrame):
            self.df = pd.concat([self.df, new_data], ignore_index=True)
        else:
            raise ValueError("New data must be a pandas DataFrame")
        self.save_dataframe()