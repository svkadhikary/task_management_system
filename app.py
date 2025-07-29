import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd

from nlp.nlp import predict_task_info
from priority_prediction.predict_priority import predict_priority
from hours_estimatror.estimate_hours import predict_hours
from assigneed_to.suggest_assignee import suggest_assignee


if 'view_added' not in st.session_state:
    st.session_state.view_added = ("", "", "")

st.set_page_config(layout="wide")

st.title("Smart Task Management System")
col_required = ["task_id", "title", "created_at", "due_date", "status", "description", "category", "type", "priority", "estimated_hours", "assignee"]

df = pd.read_csv("task_logs/tasks_data.csv", usecols=col_required) if os.path.exists(
    "task_logs/tasks_data.csv") else pd.DataFrame(
    columns=col_required
    )
for col in ["created_at", "due_date"]:
    df[col] = pd.to_datetime(df[col], errors='coerce')

st.session_state.tasks = df[(df['status'] == "To Do")].head(10)


def view_artifact(cat, type_, priority):
   prediction_placeholder = st.empty()
   with prediction_placeholder.container():
    with st.spinner('Predicting task details...'):
            time.sleep(2)  # Simulate model processing
            st.success("🎯 Auto-predicted Task Details:")
            # Display the predicted task details
            cols = st.columns(3)
            cols[0].metric("Type", type_)
            cols[1].metric("Category", cat)
            cols[2].metric("Priority", priority)
            
            # Remove after 5 seconds
    time.sleep(3)  # Display duration
    prediction_placeholder.empty()

# Sidebar for task creation
with st.sidebar:
    st.header("➕ Create New Task")
    with st.form("task_form"):
        title = st.text_input("Task Title*")
        created_at = st.date_input("Created At*", value=datetime.today(), disabled=True)
        due_date = st.date_input("Due Date*", min_value=datetime.today())
        description = st.text_area("Description")
        estimated_hours = st.number_input("Estimated Hours", min_value=0, value=1, step=1)
        submitted = st.form_submit_button("Create Task")
        if submitted:
            if not title and not description:
                st.error("All fields are required!")
            else:
                new_task = {
                    "task_id": df["task_id"].max() + 1,
                    "title": [title],
                    "created_at": [pd.to_datetime(created_at)],
                    "due_date": [pd.to_datetime(due_date)],
                    "status": ["To Do"],
                    "description": [description],
                    "estimated_hours": [estimated_hours],
                    "assignee": [""]
                }
                # Predict task category, type, and priority

                cat, type_ = predict_task_info(title + ". " + description)
                new_task["category"] = cat
                new_task["type"] = type_
                new_task['estimated_hours'] = predict_hours(pd.DataFrame(new_task))
                new_task['priority'] = predict_priority(pd.DataFrame(new_task))
                st.session_state.view_added = [cat, type_, new_task['priority']]
                df = pd.concat([df, pd.DataFrame(new_task)], ignore_index=True)
                df.to_csv("task_logs/tasks_data.csv", index=False)

                st.success("Task created successfully!")


# Main content area
if st.session_state.view_added != ("", "", ""):
    cat, type_, priority = st.session_state.view_added
    view_artifact(cat, type_, priority)
    st.session_state.view_added = ("", "", "")

col1, col2 = st.columns([4, 1])

with col2:
    st.subheader("⚡ Quick Actions")
    if st.button("Refresh Tasks"):
        st.rerun()
    
    st.metric("To Do Tasks", len(df[df["status"] == "To Do"]))
    st.metric("High Priority", len(df[df["priority"] == "High"]))

    st.write("---") # Separator for visual clarity
    st.subheader("🔍 Filter Tasks")
    # Ensure "All" option is available and values are sorted for better UX
    all_statuses = ["All"] + sorted(df['status'].unique().tolist())
    all_categories = ["All"] + sorted(df['category'].unique().tolist())
    all_types = ["All"] + sorted(df['type'].unique().tolist())
    all_priorities = ["All"] + sorted(df['priority'].unique().tolist(), key=lambda x: ['High', 'Medium', 'Low'].index(x) if x in ['High', 'Medium', 'Low'] else 99) # Custom sort for priority
    all_assignees = ["All"] + sorted(df['assignee'].dropna().unique().tolist())


    selected_status = st.selectbox("Status", all_statuses, key="filter_status")
    selected_category = st.selectbox("Category", all_categories, key="filter_category")
    selected_type = st.selectbox("Type", all_types, key="filter_type")
    selected_priority = st.selectbox("Priority", all_priorities, key="filter_priority")
    selected_assignee_filter = st.selectbox("Assigned To", all_assignees, key="filter_assignee")

    # --- Apply Filters to the DataFrame ---
    filtered_df = df.copy() # Always start with a fresh copy of the original data

    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df['type'] == selected_type]
    if selected_priority != "All":
        filtered_df = filtered_df[filtered_df['priority'] == selected_priority]
    if selected_assignee_filter != "All":
        filtered_df = filtered_df[filtered_df['assignee'] == selected_assignee_filter]

    # You can also add a search box for title/description
    search_query = st.text_input("Search Title/Description", key="filter_search_query")
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        ]

displayed_df = filtered_df
with col1:
    st.subheader("📋 Task List")
    selected_df = st.dataframe(
        displayed_df,
        use_container_width=True,
        column_config={
            "task_id": st.column_config.NumberColumn("Task ID"),
            "title": st.column_config.TextColumn("Title"),
            "created_at": st.column_config.DateColumn("Created At"),
            "due_date": st.column_config.DateColumn("Due Date"),
            "status": st.column_config.TextColumn("Status"),
            "description": st.column_config.TextColumn("Description"),
            "category": st.column_config.TextColumn("Category"),
            "type": st.column_config.TextColumn("Type"),
            "estimated_hours": st.column_config.NumberColumn("Estimated Hours"),
            "priority": st.column_config.TextColumn("Priority"),
            "assignee": st.column_config.TextColumn("Assigned To")
        },
        selection_mode="single-row",
        on_select="rerun",
        key="task_list_dataframe",
        hide_index=True
    )


    # Check if a row was selected
    if selected_df["selection"]["rows"]:
        selected_row_index = selected_df["selection"]["rows"][0]
        selected_task_id = displayed_df.iloc[selected_row_index]["task_id"]
        st.session_state.selected_task = df[df['task_id'] == selected_task_id].iloc[0].to_dict()
        st.write("---") # Separator
        st.subheader("Selected Task Details:")
        st.json(st.session_state.selected_task) # Display selected task as JSON

        # operations on the selected task
        if st.button("Mark as Complete", key="mark_complete_button"):
            # update your data source
            df.loc[df['task_id'] == selected_task_id, 'status'] = 'Completed'
            df.to_csv("task_logs/tasks_data.csv", index=False)
            # For demonstration, we'll just show a message.
            st.success(f"Task '{st.session_state.selected_task['title']}' marked as complete!")
            st.session_state.selected_task = None # Clear selection after action
            st.rerun() # Rerun to reflect changes if you update the data source

        
        # --- Corrected Edit Task Form Logic ---
        if st.button("Edit Task", key="edit_task_button"):
            # Only display the form if the button is pressed
            st.session_state.show_edit_form = True # Use a session state variable to control form visibility

        if 'show_edit_form' in st.session_state and st.session_state.show_edit_form:

            st.info(f"Opening edit form for Task: {st.session_state.selected_task['title']}")
            # open a form here to edit the task details.
            with st.form("edit_task_form"):
                new_due_date = st.date_input("New Due Date", value=st.session_state.selected_task['due_date'])
                new_status = st.selectbox("New Status", options=df.status.unique().tolist())
                initial_assignee_for_selectbox = st.session_state.suggested_assignee_value if 'suggested_assignee_value' in st.session_state else ''
                # Get all unique assignees from your DataFrame
                all_assignees = df['assignee'].dropna().unique().tolist()
                # Ensure "Unassigned" or an empty string is an option
                if "" not in all_assignees:
                    all_assignees.insert(0, "")
                all_assignees = [""] + sorted([a for a in all_assignees if a != ""]) if "" in all_assignees else sorted(all_assignees)
                # Get the current assignee for the selected task, default to empty string if not found
                current_assignee = st.session_state.selected_task.get('assignee', '')
                try:
                    default_assignee_index = all_assignees.index(initial_assignee_for_selectbox)
                except ValueError:
                    default_assignee_index = 0 # Fallback if current assignee isn't in the list
                # Create a selectbox for assignees with the current assignee pre-selected
                assigned_to = st.selectbox("Assign To",
                                           options=all_assignees,
                                           index=default_assignee_index,
                                           key='edit_assignee')
                # Add a "Suggest Assignee" button
                if st.form_submit_button("Suggest Assignee", icon="🤖"):
                    suggested = suggest_assignee(
                        df,
                        st.session_state.selected_task['category'],
                        st.session_state.selected_task['type'],
                        [a for a in all_assignees if a != ""] # Pass only actual assignees
                    )
                    # Store the suggested value in session state
                    st.session_state.suggested_assignee_value = suggested
                    st.warning(f'Suggested Assignee: **{suggested}** Click update to apply')
                    st.rerun()  # Rerun to reflect the suggested assignee
                edit_submit = st.form_submit_button("Update Task")
                if edit_submit:
                    # Update the task in the DataFrame
                    df.loc[df['task_id'] == selected_task_id, 'due_date'] = pd.to_datetime(new_due_date)
                    df.loc[df['task_id'] == selected_task_id, 'status'] = new_status
                    df.loc[df['task_id'] == selected_task_id, 'assignee'] = assigned_to
                    df.to_csv("task_logs/tasks_data.csv", index=False)
                    st.success(f"Task '{st.session_state.selected_task['title']}' updated successfully!")
                    st.session_state.selected_task = None
                    st.rerun()
