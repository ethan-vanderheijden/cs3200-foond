import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks


def get_restaurants():
    rest_data = requests.get("http://api:4000/restaurants").json()
    # logger.error(data)
    return rest_data


SideBarLinks()

st.title("Edit")

st.write("## Edit Restaurant Information")

df = pd.DataFrame(get_restaurants())
st.dataframe(df)

choose_restaurant = st.selectbox("Select a restaurant", df.iloc[:, 0])

chosen_restaurants = df[df.iloc[:, 0] == choose_restaurant].iloc[0]

restId = st.text_input("ID", value=chosen_restaurants[0])
name = st.text_input("Name", value=chosen_restaurants[1])
email = st.text_input("Email", value=chosen_restaurants[2])
phone = st.text_input("Phone", value=chosen_restaurants[3])
priceId = st.text_input("Price", value=chosen_restaurants[4])
formalityId = st.text_input("Formality", value=chosen_restaurants[5])

if st.button("Update"):
    data = {
        "id": restId,
        "name": name,
        "email": email,
        "phone": phone,
        "price_id": priceId,
        "formality_id": formalityId,
    }

    result = requests.put("http://api:4000/restaurants", json=data)

# """
# Simply retrieving data from a REST api running in a separate Docker Container.
#
# If the container isn't running, this will be very unhappy.  But the Streamlit app
# should not totally die.
# """
# data = {}
# try:
#     data = requests.get("http://api:4000/data").json()
# except Exception:
#     st.write("**Important**: Could not connect to sample api, so using dummy data.")
#     data = {"a": {"b": "123", "c": "hello"}, "z": {"b": "456", "c": "goodbye"}}
#
# st.dataframe(data)
