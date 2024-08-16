import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Edit Restaurant Information 2")

if not "state_machine" in  st.session_state:
    st.session_state["state_machine"] = 0

def state_0():
    next_state = False
    # Get the restaurant ID and view it
    with st.form(key="see_restaurant"):
        st.session_state["rest_id"] = st.text_input("Restaurant ID", "")
        submit_button = st.form_submit_button(label="See Restaurant")
        if submit_button:
            st.session_state["state_machine"] = 1
            next_state = True
    if next_state:
        st.switch_page("pages/12_Edit_Restaurant.py")

def state_1():
    next_state = False
    rest_id = st.session_state["rest_id"]
    # transform data into a visible form
    rest_data = requests.get(f"http://api:4000/restaurants/{rest_id}").json()
    with st.form(key="update_restaurant"):
        st.session_state["rest_id"] = st.text_input("resturant id", rest_id)
        st.session_state["name"] = st.text_input("name", rest_data["name"])
        st.session_state["email"] = st.text_input("email", rest_data["email"])
        st.session_state["phone"] = st.text_input("phone", rest_data["phone"])
        st.session_state["price_id"] = st.text_input("price id", rest_data["price"]["id"])
        st.session_state["formaility_id"] = st.text_input("formaility id", rest_data["formality"]["id"])

        # update values accordingly if the update button is pressed
        update_button = st.form_submit_button(label="Update")
        if update_button:
            st.session_state["state_machine"] = 2
            next_state = True
    if next_state:
        st.switch_page("pages/12_Edit_Restaurant.py")

def state_2():
    next_state = False
    rest_id = st.session_state["rest_id"]
    new_data = {
        "id": st.session_state["rest_id"],
        "name": st.session_state["name"],
        "email": st.session_state["email"],
        "phone": st.session_state["phone"],
        "priceId": st.session_state["price_id"],
        "formalityId": st.session_state["formaility_id"],
    }

    insert = requests.put(f"http://api:4000/restaurants/{rest_id}", json=new_data)

    if insert.status_code == 200:
        st.success("Restaurant updated successfully")
        next_state = True
        st.session_state["state_machine"] = 0
    else:
        st.error("Update failed")
        state_1()
    if next_state:
        st.switch_page("pages/12_Edit_Restaurant.py")


if st.session_state["state_machine"] == 0:
    state_0()
elif st.session_state["state_machine"] == 1:
    state_1()
elif st.session_state["state_machine"] == 2:
    state_2()