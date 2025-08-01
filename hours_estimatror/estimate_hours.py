import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from logger_n_exception.logger import logging

def predict_hours(tasks_desc):
    """Predicts the estimated hours for a task based on its description."""

    try:
        with open('hours_estimatror/xgb_r.pkl', 'rb') as f:
            xgb_r = pickle.load(f)
            logging.info("Loaded XGB Regressor model for hours estimation.")
    except FileNotFoundError:
        logging.error("Model file not found. Ensure the model is trained and saved correctly.")
        return "Model not found"
    
    estimate_input = tasks_desc['estimated_hours'].values
    
    for col in ['created_at', 'due_date']:
        tasks_desc[col] = pd.to_datetime(tasks_desc[col], errors='coerce')
        
    tasks_desc['expected_days'] = (tasks_desc['due_date'] - tasks_desc['created_at']).dt.days
    
    tasks_desc = tasks_desc.drop(columns=[
        'task_id', 'title', 'created_at', 'due_date', 'description', 'estimated_hours', "assignee"])
    
    minmax = MinMaxScaler()
    tasks_desc['expected_days'] = minmax.fit_transform(tasks_desc[['expected_days']])

    try:
        estimated_hours = xgb_r.predict(tasks_desc)
        logging.info(f"Predicted estimated hours: {estimated_hours} for task description.")
    except Exception as e:
        logging.error(f"Error during hours prediction: {e}")
        return "Prediction error"

    if estimate_input > 0:
        return np.round((estimated_hours + estimate_input)/2, 1)
    return np.round(estimated_hours, 1)


