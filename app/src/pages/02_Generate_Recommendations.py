import logging

logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks

USER_ID = 1


def generate_recommendation():
    st.session_state["accepted_row"] = None
    st.session_state.recommendation = requests.post(
        "http://api:4000/customers/" + str(USER_ID) + "/recommendations"
    ).json()


def accept_recommendation(row_num, rec_seq_num):
    st.session_state.accepted_row = row_num
    requests.put(
        "http://api:4000/customers/" + str(USER_ID) + "/recommendations/" + str(rec_seq_num),
        json={
            "accepted": True,
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

if "accepted_row" not in st.session_state:
    st.session_state["accepted_row"] = None

if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = None


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

    if table_df.empty:
        st.write("_Empty? [Edit your preferences](/Edit_Profile) and try to be less picky_")
    else:
        st.write("_Not what you are looking for? [Edit your preferences](/Edit_Profile)!_")

    if st.session_state.accepted_row is None and len(table_display.selection.rows) > 0:
        row_num = table_display.selection.rows[0]
        rec_seq_num = st.session_state.recommendation[row_num]["seqNum"]
        st.button(
            "Accept recommendation for id=" + str(rec_seq_num) + "?",
            use_container_width=True,
            type="primary",
            on_click=accept_recommendation,
            args=(row_num, rec_seq_num),
        )
