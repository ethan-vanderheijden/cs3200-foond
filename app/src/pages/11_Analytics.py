import streamlit as st
import requests
from modules.nav import SideBarLinks

st.title("Restaurant Analytics")

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Select category
category = st.selectbox("Select Category", ["price", "cuisine", "formality"])

# Button to fetch data
if st.button("Get Lowest Average Restaurants"):
    response = requests.get(f"http://api:4000/analytics/{category}")

    if response.status_code == 200:
        data = response.json()
        if data:
            # Show the data received
            st.write(f"Lowest Average {category.capitalize()} Score Restaurants:")
            for restaurant in data:
                st.write(f"- {restaurant['name']}: {restaurant['avg_score']}")
        else:
            st.write("No data found.")
    else:
        st.error(f"Error: {response.json().get('error')}")
