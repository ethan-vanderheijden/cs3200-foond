import streamlit as st
import requests

# Backend URL
backend_url = "http://localhost:5000/groups"


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


# Streamlit UI
st.title("Manage Groups")

action = st.selectbox(
    "Action",
    ["Create New Group", "Add User to Group", "Remove User from Group", "Display Users in Group"],
)
groupId = st.text_input("Enter Group ID")

if action == "Create New Group":
    description = st.text_input("Enter Group Description")
    if st.button("Create Group"):
        create_new_group(groupId, description)

elif action == "Add User to Group":
    user_id = st.text_input("Enter User ID to Add")
    if st.button("Add User"):
        add_user_to_group(groupId, user_id)

elif action == "Remove User from Group":
    user_id = st.text_input("Enter User ID to Remove")
    if st.button("Remove User"):
        remove_user_from_group(groupId, user_id)

elif action == "Display Users in Group":
    if st.button("Display Users"):
        display_users_in_group(groupId)
