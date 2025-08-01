import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle

def predict_hours(tasks_desc):

    with open('hours_estimatror/xgb_r.pkl', 'rb') as f:
        xgb_r = pickle.load(f)
    
    estimate_input = tasks_desc['estimated_hours'].values
    
    for col in ['created_at', 'due_date']:
        tasks_desc[col] = pd.to_datetime(tasks_desc[col], errors='coerce')
        
    tasks_desc['expected_days'] = (tasks_desc['due_date'] - tasks_desc['created_at']).dt.days
    
    tasks_desc = tasks_desc.drop(columns=[
        'task_id', 'title', 'created_at', 'due_date', 'description', 'estimated_hours', "assignee"])
    
    minmax = MinMaxScaler()
    tasks_desc['expected_days'] = minmax.fit_transform(tasks_desc[['expected_days']])

    estmated_hours = xgb_r.predict(tasks_desc)

    if estimate_input > 0:
        return np.round((estmated_hours + estimate_input)/2, 1)
    return np.round(estmated_hours, 1)


