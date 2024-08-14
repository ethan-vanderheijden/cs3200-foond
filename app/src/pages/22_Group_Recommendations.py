import logging
import streamlit as st
import requests

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Streamlit page
st.set_page_config(page_title="Group Recommendations", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state["page"] = "home"
    st.experimental_rerun()

if st.sidebar.button("Manage Groups"):
    st.session_state["page"] = "manage_groups"
    st.experimental_rerun()

if st.sidebar.button("Generate Group Recommendations"):
    st.session_state["page"] = "generate_recommendations"
    st.experimental_rerun()

if st.sidebar.button("About"):
    st.session_state["page"] = "about"
    st.experimental_rerun()

# Main content of the page
st.title("Generate Group Recommendations")

groupId = st.text_input("Enter Group ID")
if st.button("Generate Recommendations"):
    # Call the backend API to generate recommendations for the group
    response = requests.get(f"http://localhost:5000/groups/{groupId}/recommendation")
    if response.status_code == 200:
        recommendations = response.json()
        st.write(f"Recommendations for group {groupId}:")
        for rec in recommendations:
            st.write(f"- {rec['explanation']} (Restaurant ID: {rec['restId']})")
    else:
        st.error(f"Failed to generate recommendations: {response.json().get('message')}")
