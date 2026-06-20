import streamlit as st

from dashboard.ceo_briefing_view import show_ceo_briefing


st.set_page_config(
    page_title="AI CEO Strategic Intelligence Agent",
    layout="wide"
)

st.sidebar.title("AI CEO Agent")
st.sidebar.caption("Strategic Intelligence Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "CEO Briefing"
    ]
)

if page == "CEO Briefing":
    show_ceo_briefing()