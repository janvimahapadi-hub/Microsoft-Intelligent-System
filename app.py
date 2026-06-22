import streamlit as st

from dashboard.overview import show_overview
from dashboard.market_intelligence import show_market_intelligence
from dashboard.opportunity_monitor import show_opportunity_monitor
from dashboard.risk_monitor import show_risk_monitor
from dashboard.sentiment_view import show_sentiment_view
from dashboard.recommendations import show_recommendations
from dashboard.pipeline_status import show_pipeline_status
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
        "Company Overview",
        "Market Intelligence",
        "Opportunity Monitor",
        "Risk Monitor",
        "Sentiment Analysis",
        "Strategic Recommendations",
        "Data Pipeline & Refresh",
        "CEO Briefing"
    ]
)

if page == "Company Overview":
    show_overview()

elif page == "Market Intelligence":
    show_market_intelligence()

elif page == "Opportunity Monitor":
    show_opportunity_monitor()

elif page == "Risk Monitor":
    show_risk_monitor()

elif page == "Sentiment Analysis":
    show_sentiment_view()

elif page == "Strategic Recommendations":
    show_recommendations()

elif page == "Data Pipeline & Refresh":
    show_pipeline_status()

elif page == "CEO Briefing":
    show_ceo_briefing()