# Import necessary libraries
import streamlit as st
import requests
from modules.nav import SideBarLinks

# Backend URL
backend_url = "http://api:4000/groups"

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
def create_new_group(name, description=""):
    payload = {"name": name, "description": description}
    response = requests.post(backend_url, json=payload)
    if response.status_code == 201:
        new_id = response.json()["newId"]
        st.success(f"New group created with id = {new_id}. Remember this id!")
    else:
        st.error("Failed to create group")

def display_recommendation_for_my_group(groupId):
    response = requests.get(f"{backend_url}/{groupId}/recommendationsFor")
    if response.status_code == 200:
        members = response.json()
        st.write(f"Recommendation for users in group: {groupId}:")
        for member in members:
            st.write("- " + member["name"])
    else:
        st.error("Group not found " + str(response))

def display_recommendation_avoiding_group(groupId):
    response = requests.get(f"{backend_url}/{groupId}/recommendationsAvoid")
    if response.status_code == 200:
        members = response.json()
        st.write(f"Avoiding users in group: {groupId}:")
        for member in members:
            st.write("- " + member["name"])
    else:
        st.error("Group not found " + str(response.json()))

# Initialize session state for page and action
if "page_type" not in st.session_state:
    st.session_state["page_type"] = "Professor Home"
if "action" not in st.session_state:
    st.session_state.action = "Create New Group"

# Streamlit UI for Emanuel
st.title("Welcome Databasing Professor, Emanuel.")

if st.session_state["page_type"] == "Generate Group Recommendations":
    st.session_state["page_type"] = st.sidebar.selectbox(
        "Go to", ["Generate Group Recommendations", "Manage Groups"], index=0
    )
else:
    st.session_state["page_type"] = st.sidebar.selectbox(
        "Go to", ["Manage Groups", "Generate Group Recommendations"], index=0
    )

if st.session_state["page_type"] == "Manage Groups":
    st.header("Manage Groups")
    st.session_state.action = st.selectbox(
        "Action",
        [
            "Create New Group",
            "Add User to Group",
            "Remove User from Group",
            "Display Users in Group"
        ],
    )

    if st.session_state.action == "Create New Group":
        group_name = st.text_input("Enter Name")
        description = st.text_input("Enter Group Description")
        if st.button("Create Group"):
            create_new_group(group_name, description)

    elif st.session_state.action == "Add User to Group":
        groupId = st.text_input("Enter Group ID")
        user_id = st.text_input("Enter User ID to Add")
        if st.button("Add User"):
            add_user_to_group(groupId, user_id)

    elif st.session_state.action == "Remove User from Group":
        groupId = st.text_input("Enter Group ID")
        user_id = st.text_input("Enter User ID to Remove")
        if st.button("Remove User"):
            remove_user_from_group(groupId, user_id)

    elif st.session_state.action == "Display Users in Group":
        groupId = st.text_input("Enter Group ID")
        if st.button("Display Users"):
            display_users_in_group(groupId)
elif st.session_state["page_type"] == "Generate Group Recommendations":
    st.session_state["GroupType"] = st.selectbox(
        "Search Type",
        [
            "Select for my group's preferences",
            "Avoid user group",
        ],
    )
    groupId = st.text_input("Enter Group ID")
    if st.button("Display Recommendation"):
        if st.session_state["GroupType"] == "Select for my group's preferences":
            display_recommendation_for_my_group(groupId)
        elif st.session_state["GroupType"] == "Avoid user group":
            display_recommendation_avoiding_group(groupId)