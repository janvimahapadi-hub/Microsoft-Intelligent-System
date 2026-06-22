import streamlit as st

from dashboard.overview import show_overview
from dashboard.ceo_briefing_view import show_ceo_briefing
from dashboard.sentiment_view import show_sentiment
from dashboard.market_intelligence import show_market_intelligence
from dashboard.competitor_intelligence import show_competitor_intelligence
from dashboard.opportunity_monitor import show_opportunity_monitor
from dashboard.risk_monitor import show_risk_monitor
from dashboard.recommendations import show_recommendations


st.set_page_config(
    page_title="AI CEO Strategic Intelligence Agent",
    page_icon="🧠",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1rem;
    }

    .hero {
        background: linear-gradient(135deg, #1e3a8a, #2563eb, #38bdf8);
        border-radius: 22px;
        padding: 26px 32px;
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(37,99,235,0.25);
    }

    .hero h1 {
        color: white !important;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero p {
        color: white !important;
        font-size: 16px;
        margin: 0;
    }

    h1, h2, h3, h4, h5, h6,
    p, li, label, span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p,
    div[role="radiogroup"] label p {
        color: #0f172a !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800;
    }

    .stButton > button {
        background: #2563eb;
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: 700;
        padding: 0.6rem 1rem;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white !important;
    }

    div[data-testid="stExpander"] {
        background: white;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
    }

    textarea {
        background-color: white !important;
        color: #0f172a !important;
        border-radius: 12px !important;
    }

    input {
        background-color: white !important;
        color: #0f172a !important;
        border-radius: 12px !important;
    }

    div[data-testid="stCaptionContainer"] {
        color: #475569 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
        <h1>🧠 AI CEO Strategic Intelligence Agent</h1>
        <p>
        Evidence-based executive decision support using RAG, sentiment analysis,
        competitor intelligence, opportunity monitoring, risk monitoring and local LLM reasoning.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.radio(
    "Navigation",
    [
        "📊 Overview",
        "🧠 CEO Briefing",
        "📈 Sentiment",
        "🌍 Market",
        "🏁 Competitors",
        "🚀 Opportunities",
        "⚠️ Risks",
        "✅ Recommendations"
    ],
    horizontal=True
)

st.divider()

if page == "📊 Overview":
    show_overview()

elif page == "🧠 CEO Briefing":
    show_ceo_briefing()

elif page == "📈 Sentiment":
    show_sentiment()

elif page == "🌍 Market":
    show_market_intelligence()

elif page == "🏁 Competitors":
    show_competitor_intelligence()

elif page == "🚀 Opportunities":
    show_opportunity_monitor()

elif page == "⚠️ Risks":
    show_risk_monitor()

elif page == "✅ Recommendations":
    show_recommendations()