import requests
import streamlit as st
from modules.nav import SideBarLinks

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

st.title("Delete Review")

# Get the customer ID and sequence number for deletion
with st.form(key="delete_review"):
    cust_id = st.text_input("Customer ID", "")
    seq_num = st.text_input("Sequence Number", "")
    submit_button = st.form_submit_button(label="Delete Review")

if submit_button:
    try:
        # Construct the DELETE request URL
        delete_url = f"http://api:4000/reviews/{cust_id}/{seq_num}"
        response = requests.delete(delete_url)

        # Check the response status
        if response.status_code == 200:
            st.success("Review deleted successfully.")
        else:
            st.error("Failed to delete the review. Please check the inputs.")

    except Exception as e:
        st.error("An error occurred while trying to delete the review.")
