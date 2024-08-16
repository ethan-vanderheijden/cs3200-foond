import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks


# get all restaurant data from the dataset
def get_restaurants(id):
    rest_data = requests.get(f"http://api:4000/restaurants/{id}").json()
    # logger.error(data)
    return rest_data


SideBarLinks()

st.title("Edit Restaurant Information")

# Get the restaurant ID and view it
with st.form(key="see_restaurant"):
    rest_id = st.text_input("Restaurant ID", "")
    submit_button = st.form_submit_button(label="See Restaurant")

# view the restaurant if button pressed
if submit_button:
    # transform data into a visible form
    df = pd.DataFrame(get_restaurants(rest_id))
    st.dataframe(df)

    # allow user to change fields of the restaurant
    name = st.text_input("Name", value=df["name"].iloc[0])
    email = st.text_input("Email", value=df["email"].iloc[0])
    phone = st.text_input("Phone", value=df["phone"].iloc[0])
    priceId = st.text_input("Price", value=df["priceId"].iloc[0])
    formalityId = st.text_input("Formality", value=df["formalityId"].iloc[0])

    # update values accordingly if the update button is pressed
    if st.button("Update"):
        new_data = {
            "id": rest_id,
            "name": name,
            "email": email,
            "phone": phone,
            "priceId": priceId,
            "formalityId": formalityId,
        }

        insert = requests.put(f"http://api:4000/restaurants/{rest_id}", json=new_data)

        if insert.status_code == 200:
            st.success("Restaurant updated successfully")
        else:
            st.error("Update failed")
