import os
from logger_n_exception.logger import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid", palette="mako", rc={
    'axes.facecolor': (0,0,0,0), 'figure.facecolor': (0,0,0,0), 'axes.labelcolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'
    })

class VisualizationManager():
    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        self.df = df
        if self.df.empty:
            logging.warning("DataFrame is empty. No visualizations will be generated.")
    
    def plot_count(self, col, ax):
        """
        Plots the distribution of task.
        """
        sns.countplot(data=self.df, x=col, order=self.df[col].value_counts().index, ax=ax, palette='mako')
        ax.set_title(f'Distribution of {col}')
        ax.set_xlabel(f'Task {col}')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
    
    def plot_workload_per_assignee(self, display_col, assignee=None):
        """
        Plots the workload of each assignee.
        """
        logging.info(f"Plotting workload per assignee for display column: {display_col}, assignee: {assignee}")
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        axes = axes.flatten().tolist()
        for i, col in enumerate(display_col):
            if assignee:
                data = self.df[self.df['assignee'] == assignee][['assignee', col]]
            else:
                data = self.df[col]
            workload = data[col].value_counts()
            sns.countplot(data=data, x=col, ax=axes[i], order=workload.index, palette='mako')
            axes[i].set_title(f'Workload of {assignee} : {col.upper()}')
            axes[i].set_xlabel('')
            axes[i].set_ylabel('Number of Tasks')
            axes[i].tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.show()
        return fig
    
    def plot_tasks(self):
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        axes = axes.flatten().tolist()
        for i, col in enumerate(['priority', 'category', 'type', 'status']):
            self.plot_count(col, ax=axes[i])
            logging.info(f"Plotted count for {col}")
            plt.tight_layout()
        plt.show()
        return fig


