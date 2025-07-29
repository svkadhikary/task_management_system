import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import pickle
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

def predict_priority(task_data):
    """Predicts the priority of a task based on its features."""

    priorities = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
    
    # Load the pre-trained model and transformers
    with open('priority_prediction\priority_predictor.pkl', 'rb') as f:
        xgb_pipe = pickle.load(f)
    
    task_data['created_at'] = pd.to_datetime(task_data['created_at'])
    task_data['due_date'] = pd.to_datetime(task_data['due_date'])
    
    task_data['created_dow'] = task_data['created_at'].dt.dayofweek
    task_data['expected_days'] = (task_data['due_date'] - task_data['created_at']).dt.days
    task_data['is_overdue'] = (task_data['due_date'] < pd.Timestamp.now()).astype(int)
    task_data['hours_per_day'] = task_data['estimated_hours'] / task_data['expected_days'].replace(0, 1) # Avoid division by zero

    required_featuers = xgb_pipe.feature_names_in_.tolist()
    
    # Predict priority
    priority_prediction = xgb_pipe.predict(task_data[required_featuers])

    return priorities[priority_prediction[0]]

