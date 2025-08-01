import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from logger_n_exception.logger import logging

import pickle

def predict_priority(task_data):
    """Predicts the priority of a task based on its features."""

    priorities = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
    
    try:
        # Load the pre-trained model and transformers
        with open('priority_prediction\priority_predictor.pkl', 'rb') as f:
            xgb_pipe = pickle.load(f)
    except FileNotFoundError:
        logging.error("Priority prediction model file not found. Ensure the model is trained and saved correctly.")
        return "Model not found"
    
    task_data['created_at'] = pd.to_datetime(task_data['created_at'])
    task_data['due_date'] = pd.to_datetime(task_data['due_date'])
    
    task_data['created_dow'] = task_data['created_at'].dt.dayofweek
    task_data['expected_days'] = (task_data['due_date'] - task_data['created_at']).dt.days
    task_data['is_overdue'] = (task_data['due_date'] < pd.Timestamp.now()).astype(int)
    task_data['hours_per_day'] = task_data['estimated_hours'] / task_data['expected_days'].replace(0, 1) # Avoid division by zero

    required_featuers = xgb_pipe.feature_names_in_.tolist()
    
    # Predict priority
    try:
        priority_prediction = xgb_pipe.predict(task_data[required_featuers])
        logging.info(f"Predicted priority: {priority_prediction[0]} for task data: {task_data.to_dict()}")
    except Exception as e:
        logging.error(f"Error during priority prediction: {e}")
        return "Prediction error"

    return priorities[priority_prediction[0]]

