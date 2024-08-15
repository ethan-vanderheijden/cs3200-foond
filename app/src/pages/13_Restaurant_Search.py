import requests
import streamlit as st
from modules.nav import SideBarLinks

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

st.title("Search Through Restaurant Recommendations and Reviews")

# Get the restaurant ID for fetching recommendations and associated reviews
with st.form(key="fetch_recommendations_reviews"):
    restaurant_id = st.text_input("Restaurant ID", "")
    submit_button = st.form_submit_button(label="Fetch Recommendations & Reviews")

if submit_button:
    try:
        # Construct the GET request URL
        get_url = f"http://api:4000/restaurants/{restaurant_id}/reviews"
        response = requests.get(get_url)

        # Check the response status
        if response.status_code == 200:
            data = response.json()
            if data:
                st.success(f"Found {len(data)} record(s) for restaurant ID {restaurant_id}.")
                for record in data:
                    st.write(f"Restaurant Name: {record['restaurant_name']}")
                    st.write(f"Customer ID: {record['cust_id']}")
                    st.write(f"Sequence Number: {record['seq_num']}")
                    st.write(f"Recommendation: {record['recommendation']}")
                    st.write(f"Review: {record['review_text']}")
                    st.write(f"Diet Score: {record['dietScore']}")
                    st.write(f"Price Score: {record['priceScore']}")
                    st.write(f"Cuisine Score: {record['cuisineScore']}")
                    st.write(f"Formality Score: {record['formalityScore']}")
                    st.write(f"Location Score: {record['locationScore']}")
                    st.write("---")
            else:
                st.info("No recommendations or reviews found for this restaurant.")

        else:
            st.error("Failed to fetch data. Please check the Restaurant ID.")

    except Exception as e:
        st.error(f"An error occurred while trying to fetch the data: {str(e)}")
