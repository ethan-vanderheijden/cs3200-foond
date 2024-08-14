import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks

USER_ID = 1


def reset_state():
    st.session_state["accepted_row"] = None
    st.session_state["recommendation"] = None
    st.session_state["feedback_submitted"] = False


def generate_recommendation():
    reset_state()
    st.session_state.recommendation = requests.post(
        "http://api:4000/customers/" + str(USER_ID) + "/recommendations"
    ).json()


def accept_recommendation(row_num):
    st.session_state.accepted_row = row_num
    rec_seq_num = st.session_state.recommendation[row_num]["seqNum"]
    requests.put(
        "http://api:4000/customers/" + str(USER_ID) + "/recommendations/" + str(rec_seq_num),
        json={
            "accepted": True,
        },
    )


def submit_feedback():
    st.session_state.feedback_submitted = True
    rec_seq_num = st.session_state.recommendation[st.session_state.accepted_row]["seqNum"]
    requests.post(
        "http://api:4000/reviews/" + str(USER_ID) + "/" + str(rec_seq_num),
        json={
            "dietScore": st.session_state.diet_score,
            "priceScore": st.session_state.price_score,
            "cuisineScore": st.session_state.cuisine_score,
            "formalityScore": st.session_state.formality_score,
            "locationScore": st.session_state.location_score,
            "comment": st.session_state.comment,
        },
    )


SideBarLinks()

st.title("Recommendations")

st.write("Generate recommendations based on your profile")

st.button(
    "Reroll Recommendations",
    type="primary",
    use_container_width=True,
    on_click=generate_recommendation,
)

if (
    "accepted_row" not in st.session_state
    or "recommendation" not in st.session_state
    or "feedback_submitted" not in st.session_state
):
    reset_state()

if st.session_state.recommendation is not None:
    table_df = pd.DataFrame(
        [item["restId"] for item in st.session_state.recommendation], columns=["id"]
    )

    on_select = "rerun"
    styled_df = table_df
    if st.session_state.accepted_row is not None:
        on_select = "ignore"
        styled_df = table_df.style.applymap(
            lambda _: "background-color: LightGreen;",
            subset=([st.session_state.accepted_row], slice(None)),
        )
    table_display = st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select=on_select,
    )

    if st.session_state.accepted_row is None:
        if table_df.empty:
            st.write("_Empty? [Edit your preferences](/Edit_Profile) and try to be less picky_")
        else:
            st.write("_Not what you are looking for? [Edit your preferences](/Edit_Profile)!_")

        if len(table_display.selection.rows) > 0:
            row_num = table_display.selection.rows[0]
            rec_seq_num = st.session_state.recommendation[row_num]["seqNum"]
            st.button(
                "Accept recommendation for id=" + str(rec_seq_num) + "?",
                use_container_width=True,
                type="primary",
                on_click=accept_recommendation,
                args=(row_num,),
            )
    else:
        st.write("#### How was our restaurant recommendation?")
        with st.form("feedback"):
            st.write("Did the diet offerings match your preference?")
            st.feedback("stars", key="diet_score", disabled=st.session_state.feedback_submitted)
            st.write("")

            st.write("Did the price match your preference?")
            st.feedback("stars", key="price_score", disabled=st.session_state.feedback_submitted)
            st.write("")

            st.write("Did it offer the right cuisines?")
            st.feedback("stars", key="cuisine_score", disabled=st.session_state.feedback_submitted)
            st.write("")

            st.write("Did the formality match your expectations?")
            st.feedback(
                "stars", key="formality_score", disabled=st.session_state.feedback_submitted
            )
            st.write("")

            st.write("Was the restaurant in a good location?")
            st.feedback("stars", key="location_score", disabled=st.session_state.feedback_submitted)
            st.write("")

            st.text_area(
                "Additional Comment:", key="comment", disabled=st.session_state.feedback_submitted
            )

            st.form_submit_button(
                "Submit", on_click=submit_feedback, disabled=st.session_state.feedback_submitted
            )

            if st.session_state.feedback_submitted:
                st.write("##### Thank you for your feedback!")
