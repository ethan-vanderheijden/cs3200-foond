# Import necessary libraries
import streamlit as st
import requests
from modules.nav import SideBarLinks

# Backend URL
backend_url = "http://localhost:5000/groups"

# Set up the page configuration and sidebar links
st.set_page_config(layout="wide")
st.session_state["authenticated"] = False
SideBarLinks()


# Function to display users in a group
def display_users_in_group(groupId):
    response = requests.get(f"{backend_url}/{groupId}")
    if response.status_code == 200:
        members = response.json()
        st.write(f"Users in {groupId}:")
        for user in members:
            st.write(f"- {user['firstName']} {user['lastName']} ({user['email']})")
    else:
        st.error("Group not found")


# Function to add a user to a group
def add_user_to_group(groupId, user_id):
    payload = {"action": "add", "custId": user_id}
    response = requests.put(f"{backend_url}/{groupId}", json=payload)
    if response.status_code == 200:
        st.success(f"User {user_id} added to group {groupId}")
    else:
        st.error("Failed to add user to group")


# Function to remove a user from a group
def remove_user_from_group(groupId, user_id):
    payload = {"action": "remove", "custId": user_id}
    response = requests.put(f"{backend_url}/{groupId}", json=payload)
    if response.status_code == 200:
        st.success(f"User {user_id} removed from group {groupId}")
    else:
        st.error("Failed to remove user from group")


# Function to create a new group
def create_new_group(groupId, description=""):
    payload = {"name": groupId, "description": description}
    response = requests.post(backend_url, json=payload)
    if response.status_code == 201:
        st.success(f"New group {groupId} created")
    else:
        st.error("Failed to create group")


# Function to generate group recommendations
def generate_group_recommendations(groupId):
    response = requests.get(f"{backend_url}/{groupId}/recommendation")
    if response.status_code == 200:
        recommendations = response.json()
        st.write(f"Recommendations for Group {groupId}:")
        for rec in recommendations:
            st.write(f"- {rec['explanation']} (Restaurant ID: {rec['restId']})")
    else:
        st.error("Failed to generate recommendations")


# Initialize session state for page and action
if "page" not in st.session_state:
    st.session_state.page = "Professor Home"
if "action" not in st.session_state:
    st.session_state.action = "Create New Group"

# Streamlit UI for Emanuel
st.title("Welcome Databasing Professor, Emanuel.")

st.sidebar.header("Navigation")
st.session_state.page = st.sidebar.selectbox(
    "Go to", ["Manage Groups", "Generate Group Recommendations"], index=0
)

if st.session_state.page == "Manage Groups":
    st.header("Manage Groups")
    st.session_state.action = st.selectbox(
        "Action",
        [
            "Create New Group",
            "Add User to Group",
            "Remove User from Group",
            "Display Users in Group",
        ],
    )

    groupId = st.text_input("Enter Group ID")

    if st.session_state.action == "Create New Group":
        description = st.text_input("Enter Group Description")
        if st.button("Create Group"):
            create_new_group(groupId, description)

    elif st.session_state.action == "Add User to Group":
        user_id = st.text_input("Enter User ID to Add")
        if st.button("Add User"):
            add_user_to_group(groupId, user_id)

    elif st.session_state.action == "Remove User from Group":
        user_id = st.text_input("Enter User ID to Remove")
        if st.button("Remove User"):
            remove_user_from_group(groupId, user_id)

    elif st.session_state.action == "Display Users in Group":
        if st.button("Display Users"):
            display_users_in_group(groupId)

elif st.session_state.page == "Generate Group Recommendations":
    st.header("Generate Group Recommendations")
    groupId = st.text_input("Enter Group ID")
    if st.button("Generate Recommendations"):
        generate_group_recommendations(groupId)

if st.sidebar.button("Logout"):
    st.write("You have been logged out.")  # In a real app, handle the logout process properly
