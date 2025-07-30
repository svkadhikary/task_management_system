import pandas as pd
import numpy as np


def suggest_assignee(df, task_category, task_type, task_id, current_assignees_list):
    """
    Suggests an assignee based on:
    1. Historical expertise (who handled similar categories/types).
    2. Current workload (fewer 'To Do' tasks).
    """
    if not current_assignees_list:
        return "Unassigned" # No assignees available

    if "" in current_assignees_list:
        current_assignees_list.remove("")

    # 1. Calculate current workload for each assignee
    assignee_workload = df[df['status'] == 'To Do']['assignee'].value_counts().to_dict()
    # Check all assignee work hours per day work
    df['expected_days'] = (pd.to_datetime(df['due_date']) - pd.to_datetime(df['created_at'])).dt.days
    df['hours_per_day'] = df['estimated_hours'] / df['expected_days'].replace(0, np.nan) # Avoid division by zero
    assignee_hours_per_day = df[df['status'] == 'To Do'].groupby('assignee')['hours_per_day'].mean().to_dict()

    print("Assignee workload:", assignee_workload)
    print("Assignee hours per day:", assignee_hours_per_day)
    
    for assignee in current_assignees_list:
        assignee_workload.setdefault(assignee, 0) # Ensure all current assignees are in the dict, even if they have no tasks

    # 2. Find assignees with expertise in the given category/type
    expert_assignees = []
    # Find who has completed tasks of this category/type
    relevant_tasks = df[(df['category'] == task_category) & (df['type'] == task_type) & (df['status'] == 'Completed')]
    if not relevant_tasks.empty:
        expert_assignees = relevant_tasks['assignee'].dropna().unique().tolist()
    
    print("Expert assignees found:", expert_assignees)
    # If no one has completed this specific category/type,
    # fall back to anyone who has completed this category
    if not expert_assignees:
        relevant_tasks = df[(df['category'] == task_category) & (df['status'] == 'Completed')]
        if not relevant_tasks.empty:
            expert_assignees = relevant_tasks['assignee'].unique().tolist()

    # Filter experts to only include current_assignees_list
    expert_assignees = [a for a in expert_assignees if a in current_assignees_list]

    hours_per_day_threshold = 10 # Example threshold for work hours per day
    estimated_hours_per_day = df[df['task_id'] == task_id]['hours_per_day'].values[0]
    if expert_assignees:
        # Among experts, pick the one with the least workload
        min_workload = float('inf')
        best_assignee = None
        for assignee in expert_assignees:
            workload = assignee_workload.get(assignee, 0)
            workhours_per_day = assignee_hours_per_day.get(assignee, 0)
            if workload < min_workload:
                if workhours_per_day+estimated_hours_per_day < hours_per_day_threshold:
                    min_workload = workload
                    best_assignee = assignee
        print("Best expert assignee found:", best_assignee)
        return best_assignee
    else:
        # If no expert found, pick the one with the least workload overall
        min_workload = float('inf')
        best_assignee = None
        for assignee in current_assignees_list:
            workload = assignee_workload.get(assignee, 0)
            workhours_per_day = assignee_hours_per_day.get(assignee, 0)
            if workload < min_workload:
                if workhours_per_day + estimated_hours_per_day < hours_per_day_threshold:
                    min_workload = workload
                    best_assignee = assignee
        print("Best non-expert assignee found:", best_assignee)
        return best_assignee or current_assignees_list[0] # Fallback to first if all workloads are infinite (e.g. empty)
    