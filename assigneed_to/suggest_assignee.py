


def suggest_assignee(df, task_category, task_type, current_assignees_list):
    """
    Suggests an assignee based on:
    1. Historical expertise (who handled similar categories/types).
    2. Current workload (fewer 'To Do' tasks).
    """
    if not current_assignees_list:
        return "Unassigned" # No assignees available

    # 1. Calculate current workload for each assignee
    assignee_workload = df[df['status'] == 'To Do']['assignee'].value_counts().to_dict()
    for assignee in current_assignees_list:
        assignee_workload.setdefault(assignee, 0) # Ensure all current assignees are in the dict, even if they have no tasks

    # 2. Find assignees with expertise in the given category/type
    expert_assignees = []
    # Find who has completed tasks of this category/type
    relevant_tasks = df[(df['category'] == task_category) & (df['type'] == task_type) & (df['status'] == 'Completed')]
    if not relevant_tasks.empty:
        expert_assignees = relevant_tasks['assignee'].dropna().unique().tolist()
    
    # If no one has completed this specific category/type,
    # fall back to anyone who has completed this category
    if not expert_assignees:
        relevant_tasks = df[(df['category'] == task_category) & (df['status'] == 'Completed')]
        if not relevant_tasks.empty:
            expert_assignees = relevant_tasks['assignee'].unique().tolist()

    # Filter experts to only include current_assignees_list
    expert_assignees = [a for a in expert_assignees if a in current_assignees_list]

    if expert_assignees:
        # Among experts, pick the one with the least workload
        min_workload = float('inf')
        best_assignee = None
        for assignee in expert_assignees:
            workload = assignee_workload.get(assignee, 0)
            if workload < min_workload:
                min_workload = workload
                best_assignee = assignee
        return best_assignee
    else:
        # If no expert found, pick the one with the least workload overall
        min_workload = float('inf')
        best_assignee = None
        for assignee in current_assignees_list:
            workload = assignee_workload.get(assignee, 0)
            if workload < min_workload:
                min_workload = workload
                best_assignee = assignee
        return best_assignee or current_assignees_list[0] # Fallback to first if all workloads are infinite (e.g. empty)