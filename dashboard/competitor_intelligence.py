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


def show_competitor_intelligence():
    st.title("Competitor Intelligence")
    st.caption(
        "Compare Microsoft with AWS, Google Cloud, OpenAI, NVIDIA, and other competitor intelligence sources."
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
    clean_df = df[df["strategic_signal"] != "Irrelevant"].copy()

    companies = sorted(clean_df["company_view"].dropna().unique().tolist())

    microsoft_docs = int((clean_df["company_view"] == "Microsoft").sum())
    competitor_docs = len(clean_df) - microsoft_docs
    opportunities = int((clean_df["strategic_signal"] == "Opportunity").sum())
    risks = int((clean_df["strategic_signal"] == "Risk").sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Companies Tracked", len(companies))
    col2.metric("Competitor Docs", competitor_docs)
    col3.metric("Opportunity Signals", opportunities)
    col4.metric("Risk Signals", risks)

    st.divider()

    st.subheader("Company Coverage")
    st.bar_chart(clean_df["company_view"].value_counts())

    st.subheader("Opportunity vs Risk by Company")

    signal_company = (
        clean_df.groupby(["company_view", "strategic_signal"])
        .size()
        .reset_index(name="count")
    )

    signal_pivot = signal_company.pivot(
        index="company_view",
        columns="strategic_signal",
        values="count"
    ).fillna(0)

    st.bar_chart(signal_pivot)

    st.subheader("Sentiment by Company")

    sentiment_company = (
        clean_df.groupby(["company_view", "sentiment"])
        .size()
        .reset_index(name="count")
    )

    sentiment_pivot = sentiment_company.pivot(
        index="company_view",
        columns="sentiment",
        values="count"
    ).fillna(0)

    st.bar_chart(sentiment_pivot)

    st.divider()

    st.subheader("Strategic Comparison Table")

    comparison = (
        clean_df.groupby("company_view")
        .agg(
            documents=("title", "count"),
            sources=("source", "nunique"),
            topics=("topic", "nunique"),
            avg_sentiment_score=("sentiment_score", "mean"),
        )
        .reset_index()
    )

    opportunity_counts = (
        clean_df[clean_df["strategic_signal"] == "Opportunity"]
        .groupby("company_view")
        .size()
        .reset_index(name="opportunities")
    )

    risk_counts = (
        clean_df[clean_df["strategic_signal"] == "Risk"]
        .groupby("company_view")
        .size()
        .reset_index(name="risks")
    )

    comparison = comparison.merge(
        opportunity_counts,
        on="company_view",
        how="left"
    ).merge(
        risk_counts,
        on="company_view",
        how="left"
    )

    comparison["opportunities"] = comparison["opportunities"].fillna(0).astype(int)
    comparison["risks"] = comparison["risks"].fillna(0).astype(int)
    comparison["avg_sentiment_score"] = comparison["avg_sentiment_score"].round(3)

    comparison = comparison.sort_values(
        by="documents",
        ascending=False
    )

    st.dataframe(comparison, use_container_width=True)

    st.divider()

    st.subheader("Company Deep Dive")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + companies
    )

    selected_signal = st.selectbox(
        "Select strategic signal",
        ["All"] + sorted(clean_df["strategic_signal"].dropna().unique().tolist())
    )

    selected_topic = st.selectbox(
        "Select topic",
        ["All"] + sorted(clean_df["topic"].dropna().unique().tolist())
    )

    filtered_df = clean_df.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_signal != "All":
        filtered_df = filtered_df[filtered_df["strategic_signal"] == selected_signal]

    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df["topic"] == selected_topic]

    st.write(f"Showing {len(filtered_df)} documents")

    for _, row in filtered_df.head(30).iterrows():
        with st.expander(row["title"]):
            st.write("**Company:**", row["company_view"])
            st.write("**Source:**", row["source"])
            st.write("**Topic:**", row.get("topic", "Unknown"))
            st.write("**Sentiment:**", row.get("sentiment", "Unknown"))
            st.write("**Sentiment Score:**", row.get("sentiment_score", "Unknown"))
            st.write("**Strategic Signal:**", row.get("strategic_signal", "Unknown"))
            st.write("**Signal Strength:**", row.get("signal_strength", "Unknown"))

            if row.get("url"):
                st.markdown(f"**URL:** [{row['url']}]({row['url']})")

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
                This page compares Microsoft intelligence with competitor activity.
            </p>

            <ul>
                <li style="color:#0f172a;">High competitor opportunity signals show where rivals are investing aggressively.</li>
                <li style="color:#0f172a;">Risk signals show where companies may face governance, security, regulatory, or execution challenges.</li>
                <li style="color:#0f172a;">The comparison table helps identify which companies dominate the current evidence base.</li>
                <li style="color:#0f172a;">This supports executive questions such as: where should Microsoft defend, where should it invest, and which competitors require monitoring?</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )