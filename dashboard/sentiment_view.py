import json

import pandas as pd
import streamlit as st


SENTIMENT_PATH = "data/sentiment_results.json"


def load_sentiment_data():
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


def show_sentiment():
    st.title("Sentiment Intelligence")
    st.caption(
        "Sentiment, topic, company, and strategic signal analysis over collected intelligence documents."
    )

    data = load_sentiment_data()

    if not data:
        st.warning("No sentiment data found. Run sentiment/sentiment_analyzer.py first.")
        return

    df = pd.DataFrame(data)

    if "strategic_signal" not in df.columns:
        st.warning("Run sentiment/strategic_classifier.py first.")
        return

    if "signal_strength" not in df.columns:
        df["signal_strength"] = "Unknown"

    df["company_view"] = df.apply(get_company, axis=1)

    clean_df = df[df["strategic_signal"] != "Irrelevant"].copy()

    total_docs = len(clean_df)
    positive = int((clean_df["sentiment"] == "Positive").sum())
    negative = int((clean_df["sentiment"] == "Negative").sum())
    companies = clean_df["company_view"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Relevant Documents", total_docs)
    col2.metric("Positive", positive)
    col3.metric("Negative", negative)
    col4.metric("Companies", companies)

    st.divider()

    st.subheader("Sentiment Distribution")
    st.bar_chart(clean_df["sentiment"].value_counts())

    st.subheader("Strategic Signal Distribution")
    st.bar_chart(clean_df["strategic_signal"].value_counts())

    st.subheader("Topic Distribution")
    st.bar_chart(clean_df["topic"].value_counts())

    st.divider()

    st.subheader("Sentiment by Company")

    sentiment_company = (
        clean_df.groupby(["company_view", "sentiment"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(sentiment_company, use_container_width=True)

    st.subheader("Strategic Signal by Company")

    signal_company = (
        clean_df.groupby(["company_view", "strategic_signal"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(signal_company, use_container_width=True)

    st.subheader("Topic by Company")

    topic_company = (
        clean_df.groupby(["company_view", "topic"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(topic_company, use_container_width=True)

    st.divider()

    st.subheader("Filter Documents")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + sorted(clean_df["company_view"].dropna().unique().tolist())
    )

    selected_topic = st.selectbox(
        "Select topic",
        ["All"] + sorted(clean_df["topic"].dropna().unique().tolist())
    )

    selected_sentiment = st.selectbox(
        "Select sentiment",
        ["All"] + sorted(clean_df["sentiment"].dropna().unique().tolist())
    )

    selected_signal = st.selectbox(
        "Select strategic signal",
        ["All"] + sorted(clean_df["strategic_signal"].dropna().unique().tolist())
    )

    filtered_df = clean_df.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df["topic"] == selected_topic]

    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]

    if selected_signal != "All":
        filtered_df = filtered_df[filtered_df["strategic_signal"] == selected_signal]

    st.write(f"Showing {len(filtered_df)} documents")

    for _, row in filtered_df.head(30).iterrows():
        with st.expander(row["title"]):
            st.write("**Company:**", row["company_view"])
            st.write("**Source:**", row["source"])
            st.write("**Source Type:**", row.get("source_type", "unknown"))
            st.write("**Topic:**", row["topic"])
            st.write("**Sentiment:**", row["sentiment"])
            st.write("**Sentiment Score:**", row["sentiment_score"])
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
                This page explains how sentiment and strategic signals are distributed across companies and topics.
            </p>

            <ul>
                <li style="color:#0f172a;">Positive sentiment can indicate opportunity, adoption, or product momentum.</li>
                <li style="color:#0f172a;">Negative sentiment can indicate risk, criticism, uncertainty, or security concern.</li>
                <li style="color:#0f172a;">Company-level sentiment helps compare Microsoft with AWS, Google Cloud, OpenAI, and NVIDIA.</li>
                <li style="color:#0f172a;">Strategic signals convert raw sentiment into business categories such as opportunity, risk, or neutral.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )