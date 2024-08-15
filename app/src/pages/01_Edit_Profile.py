import logging

logger = logging.getLogger(__name__)
import requests
import streamlit as st
from modules.nav import SideBarLinks

USER_ID = 1


@st.cache_data
def get_available_preferences():
    return requests.get("http://api:4000/preferences").json()


def update_profile_data():
    requests.put(
        "http://api:4000/customers/" + str(USER_ID),
        json={
            "firstName": st.session_state.first,
            "middleInitial": st.session_state.mi,
            "lastName": st.session_state.last,
            "email": st.session_state.email,
            "longitude": st.session_state.longitude,
            "latitude": st.session_state.latitude,
            "pricePreferences": st.session_state.prices,
            "cuisinePreferences": st.session_state.cuisines,
            "dietPreferences": st.session_state.diets,
            "formalityPreferences": st.session_state.formalities,
        },
    )


# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

st.title("Update Profile + Preferences")

user_data = requests.get("http://api:4000/customers/" + str(USER_ID)).json()

pref_data = get_available_preferences()

prices = pref_data["prices"]
cuisines = pref_data["cuisines"]
diets = pref_data["diets"]
formalities = pref_data["formalities"]

with st.form("update_profile"):
    st.write("#### Basic Info")

    st.text_input("First Name:", value=user_data["firstName"], key="first")
    st.text_input("Middle Initial:", value=user_data["middleInitial"], max_chars=1, key="mi")
    st.text_input("Last Name:", value=user_data["lastName"], key="last")
    st.text_input("Email:", value=user_data["email"], key="email")
    st.number_input(
        "Longitude:",
        min_value=-180.0,
        max_value=180.0,
        value=user_data["longitude"],
        step=1e-6,
        format="%.6f",
        key="longitude",
    )
    st.number_input(
        "Latitude:",
        min_value=-180.0,
        max_value=180.0,
        value=user_data["latitude"],
        step=1e-6,
        format="%.6f",
        key="latitude",
    )

    st.write("#### Preferences")

    def format_price(price_id):
        return f"${prices[price_id]['rating']}: {prices[price_id]['description']}"

    current_price_pref = [str(p) for p in user_data["prices"]]
    st.multiselect(
        "Prices", prices.keys(), current_price_pref, format_func=format_price, key="prices"
    )

    def create_multiselect(label, key, prefs, default_data):
        def format_pref(pref_id):
            return f"{prefs[pref_id]['name']} - {prefs[pref_id]['description']}"

        formatted_default_data = [str(p) for p in default_data]
        st.multiselect(
            label, prefs.keys(), formatted_default_data, format_func=format_pref, key=key
        )

    create_multiselect("Cuisines", "cuisines", cuisines, user_data["cuisine"])
    create_multiselect("Diets", "diets", diets, user_data["diet"])
    create_multiselect("Formality", "formalities", formalities, user_data["formality"])

    st.form_submit_button("Update", on_click=update_profile_data)
