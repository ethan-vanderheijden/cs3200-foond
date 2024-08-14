import logging
import streamlit as st
import requests

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Streamlit page
st.set_page_config(page_title="Group Management", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state["page"] = "home"
    st.experimental_rerun()

# Main content of the page
st.title("Manage Groups")

# Action selection
action = st.selectbox(
    "Select Action",
    ["Create New Group", "Add User to Group", "Remove User from Group", "Display Users in Group"],
)

# Group ID input
groupId = st.text_input("Enter Group ID")

# Based on the selected action, provide different functionalities
if action == "Create New Group":
    description = st.text_input("Enter Group Description")
    if st.button("Create Group"):
        # Call the backend API to create a new group
        response = requests.post(
            f"http://localhost:5000/groups", json={"name": groupId, "description": description}
        )
        if response.status_code == 201:
            st.success(f"Group '{groupId}' created successfully.")
        else:
            st.error(f"Failed to create group: {response.json().get('message')}")

elif action == "Add User to Group":
    user_id = st.text_input("Enter User ID to Add")
    if st.button("Add User"):
        # Call the backend API to add a user to the group
        response = requests.put(
            f"http://localhost:5000/groups/{groupId}", json={"action": "add", "custId": user_id}
        )
        if response.status_code == 200:
            st.success(f"User {user_id} added to group {groupId}.")
        else:
            st.error(f"Failed to add user to group: {response.json().get('message')}")

elif action == "Remove User from Group":
    user_id = st.text_input("Enter User ID to Remove")
    if st.button("Remove User"):
        # Call the backend API to remove a user from the group
        response = requests.put(
            f"http://localhost:5000/groups/{groupId}", json={"action": "remove", "custId": user_id}
        )
        if response.status_code == 200:
            st.success(f"User {user_id} removed from group {groupId}.")
        else:
            st.error(f"Failed to remove user from group: {response.json().get('message')}")

elif action == "Display Users in Group":
    if st.button("Display Users"):
        # Call the backend API to get users in the group
        response = requests.get(f"http://localhost:5000/groups/{groupId}")
        if response.status_code == 200:
            members = response.json()
            st.write(f"Users in group {groupId}:")
            for member in members:
                st.write(f"- {member['firstName']} {member['lastName']} ({member['email']})")
        else:
            st.error(f"Failed to retrieve users: {response.json().get('message')}")
