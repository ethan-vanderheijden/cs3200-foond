import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks


def get_restaurants(id):
    rest_data = requests.get(f"http://api:4000/restaurants/{id}").json()
    # logger.error(data)
    return rest_data


SideBarLinks()

st.title("Edit")

st.write("## Edit Restaurant Information")

# Get the customer ID and sequence number for deletion
with st.form(key="see_resturant"):
    rest_id = st.text_input("Restaurant ID", "")
    submit_button = st.form_submit_button(label="See Restaurant")
if submit_button:
    df = pd.DataFrame(get_restaurants(rest_id))
    st.dataframe(df)