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


def show_opportunity_monitor():
    st.title("Opportunity Monitor")
    st.caption(
        "Tracks opportunity signals across Microsoft and competitor intelligence sources."
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

    opportunities = df[df["strategic_signal"] == "Opportunity"].copy()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Opportunity Documents", len(opportunities))
    col2.metric(
        "Positive Opportunities",
        int((opportunities["sentiment"] == "Positive").sum())
    )
    col3.metric("Opportunity Topics", opportunities["topic"].nunique())
    col4.metric("Companies", opportunities["company_view"].nunique())

    st.divider()

    st.subheader("Opportunities by Company")
    st.bar_chart(opportunities["company_view"].value_counts())

    st.subheader("Opportunity Topics")
    st.bar_chart(opportunities["topic"].value_counts())

    st.subheader("Opportunities by Source")
    st.bar_chart(opportunities["source"].value_counts())

    st.divider()

    st.subheader("Opportunity Intelligence Table")

    opportunity_table = (
        opportunities.groupby(["company_view", "topic"])
        .size()
        .reset_index(name="opportunity_count")
        .sort_values("opportunity_count", ascending=False)
    )

    st.dataframe(opportunity_table, use_container_width=True)

    st.divider()

    st.subheader("Filter Opportunities")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + sorted(opportunities["company_view"].dropna().unique().tolist())
    )

    selected_topic = st.selectbox(
        "Select opportunity topic",
        ["All"] + sorted(opportunities["topic"].dropna().unique().tolist())
    )

    filtered_df = opportunities.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df["topic"] == selected_topic]

    filtered_df = filtered_df.sort_values(
        by="sentiment_score",
        ascending=False
    )

    st.write(f"Showing {len(filtered_df)} opportunity documents")

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
                "This document was classified as an opportunity signal because it contains language related to "
                "growth, adoption, AI platforms, cloud infrastructure, partnerships, automation, or enterprise value."
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
                This page highlights where business opportunity signals are appearing across Microsoft and competitors.
            </p>

            <ul>
                <li style="color:#0f172a;">Microsoft opportunity signals show areas where it can scale existing strengths.</li>
                <li style="color:#0f172a;">Competitor opportunity signals show where rivals may be gaining momentum.</li>
                <li style="color:#0f172a;">Topic-level opportunity analysis helps identify which markets deserve executive attention.</li>
                <li style="color:#0f172a;">Strong opportunity clusters can guide product investment, partner strategy, and go-to-market planning.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )