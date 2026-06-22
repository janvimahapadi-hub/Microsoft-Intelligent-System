import json

import pandas as pd
import streamlit as st


SENTIMENT_PATH = "data/sentiment_results.json"


def load_data():
    with open(SENTIMENT_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_company(row):
    company = row.get("company", "")
    competitor = row.get("competitor", "")
    source = row.get("source", "")

    if company:
        return company

    if competitor:
        return competitor

    source_lower = source.lower()

    if "aws" in source_lower:
        return "AWS"
    if "google" in source_lower:
        return "Google Cloud"
    if "openai" in source_lower:
        return "OpenAI"
    if "nvidia" in source_lower:
        return "NVIDIA"

    return "Microsoft"


def show_risk_monitor():
    st.title("Risk Monitor")
    st.caption(
        "Tracks risk signals across Microsoft and competitor intelligence sources."
    )

    data = load_data()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No sentiment data found.")
        return

    if "strategic_signal" not in df.columns:
        st.warning("Run sentiment/strategic_classifier.py first.")
        return

    df["company_view"] = df.apply(get_company, axis=1)

    risks = df[df["strategic_signal"] == "Risk"].copy()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Risk Documents", len(risks))
    col2.metric(
        "Negative Risks",
        int((risks["sentiment"] == "Negative").sum())
    )
    col3.metric("Risk Topics", risks["topic"].nunique())
    col4.metric("Companies", risks["company_view"].nunique())

    st.divider()

    st.subheader("Risks by Company")
    st.bar_chart(risks["company_view"].value_counts())

    st.subheader("Risk Topics")
    st.bar_chart(risks["topic"].value_counts())

    st.subheader("Risks by Source")
    st.bar_chart(risks["source"].value_counts())

    st.divider()

    st.subheader("Risk Intelligence Table")

    risk_table = (
        risks.groupby(["company_view", "topic"])
        .size()
        .reset_index(name="risk_count")
        .sort_values("risk_count", ascending=False)
    )

    st.dataframe(risk_table, use_container_width=True)

    st.divider()

    st.subheader("Filter Risks")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + sorted(risks["company_view"].dropna().unique().tolist())
    )

    selected_topic = st.selectbox(
        "Select risk topic",
        ["All"] + sorted(risks["topic"].dropna().unique().tolist())
    )

    filtered_df = risks.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df["topic"] == selected_topic]

    filtered_df = filtered_df.sort_values(
        by="sentiment_score",
        ascending=False
    )

    st.write(f"Showing {len(filtered_df)} risk documents")

    for _, row in filtered_df.head(30).iterrows():
        with st.expander(row["title"]):
            st.write("**Company:**", row["company_view"])
            st.write("**Source:**", row["source"])
            st.write("**Topic:**", row["topic"])
            st.write("**Sentiment:**", row["sentiment"])
            st.write("**Sentiment Score:**", row["sentiment_score"])
            st.write("**Signal Strength:**", row.get("signal_strength", "Unknown"))

            if row.get("url"):
                st.markdown(f"**URL:** [{row['url']}]({row['url']})")

            st.write("**Why this matters:**")
            st.write(
                "This document was classified as a risk signal because it contains language related to "
                "security, threats, governance, compliance, competition, privacy, cost, regulation, or operational challenges."
            )

            st.write("**Preview:**")
            st.write(row.get("preview", ""))

    st.divider()

    st.subheader("Executive Interpretation")

    st.markdown(
        """
        <div style="
            background-color: white;
            color: #0f172a;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
            font-size: 16px;
            line-height: 1.7;
        ">
            <p style="color:#0f172a;">
                This page highlights strategic risk signals across Microsoft and competitor intelligence.
            </p>

            <ul>
                <li style="color:#0f172a;">Microsoft risk signals show areas requiring internal attention, governance, or mitigation.</li>
                <li style="color:#0f172a;">Competitor risk signals show where rivals may face weaknesses or regulatory pressure.</li>
                <li style="color:#0f172a;">Security and governance risks are especially important because enterprise AI adoption depends on trust.</li>
                <li style="color:#0f172a;">Risk clusters can guide executive decisions around compliance, cybersecurity, product safety, and market positioning.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )