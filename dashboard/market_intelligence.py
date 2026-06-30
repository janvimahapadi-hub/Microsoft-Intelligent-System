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
    if "anthropic" in source_lower:
        return "Anthropic"

    return "Microsoft"


def prepare_dates(df):
    if "published" not in df.columns:
        df["published_date"] = pd.NaT
        df["month"] = "Unknown"
        return df

    df["published_date"] = pd.to_datetime(
        df["published"],
        errors="coerce",
        utc=True
    )

    df["month"] = df["published_date"].dt.to_period("M").astype(str)
    df["month"] = df["month"].replace("NaT", "Unknown")

    return df


def show_latest_news(df):
    st.subheader("Recent News")

    latest = (
        df.sort_values("published_date", ascending=False)
        .head(5)
    )

    for _, row in latest.iterrows():
        st.markdown(f"**{row.get('title', 'Untitled')}**")
        st.caption(
            f"{row.get('source', 'Unknown source')} | "
            f"{row.get('published', 'unknown')} | "
            f"{row.get('topic', 'Unknown topic')}"
        )


def show_competitor_activities(df):
    st.subheader("Competitor Activities")

    competitors = df[df["company_view"] != "Microsoft"].head(8)

    if competitors.empty:
        st.info("No competitor activities found.")
        return

    for _, row in competitors.iterrows():
        st.markdown(
            f"**{row.get('company_view', 'Unknown')}** — "
            f"{row.get('title', 'Untitled')}"
        )
        st.caption(
            f"{row.get('source', 'Unknown source')} | "
            f"{row.get('topic', 'Unknown topic')} | "
            f"{row.get('strategic_signal', 'Unknown signal')}"
        )


def show_emerging_technologies(df):
    st.subheader("Emerging Technologies")

    tech_keywords = [
        "AI",
        "Copilot",
        "Azure",
        "Agent",
        "Foundry",
        "LLM",
        "Cloud",
        "Security",
        "Developer",
        "Infrastructure",
        "Model",
        "Automation",
        "Data",
        "Governance"
    ]

    text_series = (
        df.get("title", pd.Series(dtype=str)).fillna("").astype(str)
        + " "
        + df.get("evidence", pd.Series(dtype=str)).fillna("").astype(str)
    )

    found = []

    for keyword in tech_keywords:
        count = text_series.str.contains(keyword, case=False, regex=False).sum()

        if count > 0:
            found.append((keyword, int(count)))

    if found:
        tech_df = pd.DataFrame(found, columns=["Technology", "Mentions"])
        tech_df = tech_df.sort_values("Mentions", ascending=False)
        st.bar_chart(tech_df.set_index("Technology"))
        st.dataframe(tech_df, use_container_width=True)
    else:
        st.info("No emerging technology signals found.")


def show_company_announcements(df):
    st.subheader("Important Company Announcements")

    announcements = (
        df[df["company_view"] == "Microsoft"]
        .sort_values("published_date", ascending=False)
        .head(5)
    )

    if announcements.empty:
        st.info("No Microsoft announcements found.")
        return

    for _, row in announcements.iterrows():
        st.markdown(f"**{row.get('title', 'Untitled')}**")
        st.caption(
            f"{row.get('source', 'Unknown source')} | "
            f"{row.get('published', 'unknown')} | "
            f"{row.get('topic', 'Unknown topic')} | "
            f"{row.get('strategic_signal', 'Unknown signal')}"
        )


def show_market_intelligence():
    st.title("Market Intelligence")
    st.caption(
        "Aggregated view of topics, sources, sentiment, strategic signals, competitors, and trends."
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
    clean_df = prepare_dates(clean_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Relevant Docs", len(clean_df))
    col2.metric("Companies", clean_df["company_view"].nunique())
    col3.metric("Topics", clean_df["topic"].nunique())
    col4.metric("Sources", clean_df["source"].nunique())

    st.divider()

    st.subheader("Market Coverage by Company")
    st.bar_chart(clean_df["company_view"].value_counts())

    st.subheader("Most Discussed Topics")
    st.bar_chart(clean_df["topic"].value_counts())

    st.subheader("Source Coverage")
    st.bar_chart(clean_df["source"].value_counts())

    st.divider()

    st.subheader("Trend Intelligence")
    st.caption(
        "Tracks document volume, sentiment, and opportunity/risk signals over time."
    )

    trend_df = clean_df[clean_df["month"] != "Unknown"].copy()

    if trend_df.empty:
        st.info(
            "No valid publication dates found for trend charts. "
            "Trend intelligence becomes stronger as more dated sources are collected."
        )
    else:
        st.markdown("### Document Volume Over Time")

        volume_trend = (
            trend_df.groupby("month")
            .size()
            .reset_index(name="documents")
            .sort_values("month")
        )

        st.line_chart(volume_trend, x="month", y="documents")

        st.markdown("### Sentiment Trend Over Time")

        sentiment_trend = (
            trend_df.groupby(["month", "sentiment"])
            .size()
            .reset_index(name="count")
            .sort_values("month")
        )

        sentiment_pivot = sentiment_trend.pivot(
            index="month",
            columns="sentiment",
            values="count"
        ).fillna(0)

        st.line_chart(sentiment_pivot)

        st.markdown("### Opportunity vs Risk Trend")

        signal_trend = (
            trend_df.groupby(["month", "strategic_signal"])
            .size()
            .reset_index(name="count")
            .sort_values("month")
        )

        signal_pivot = signal_trend.pivot(
            index="month",
            columns="strategic_signal",
            values="count"
        ).fillna(0)

        st.line_chart(signal_pivot)

    st.divider()

    st.subheader("Sentiment by Company")

    sentiment_by_company = (
        clean_df.groupby(["company_view", "sentiment"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(sentiment_by_company, use_container_width=True)

    st.subheader("Strategic Signal by Company")

    signal_by_company = (
        clean_df.groupby(["company_view", "strategic_signal"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(signal_by_company, use_container_width=True)

    st.subheader("Topic vs Strategic Signal")

    topic_signal = (
        clean_df.groupby(["topic", "strategic_signal"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(topic_signal, use_container_width=True)

    st.divider()

    st.subheader("Market Interpretation")

    with st.container(border=True):
        st.write(
            "This page compares market signals across Microsoft and competitor sources."
        )

        st.markdown(
            """
- **Company coverage** shows whether the intelligence base is balanced across Microsoft, AWS, Google Cloud, OpenAI, NVIDIA, and others.
- **Trend intelligence** shows whether document volume, sentiment, risks, or opportunities are changing over time.
- **High opportunity signals** suggest areas where companies are investing aggressively.
- **High risk signals** suggest areas requiring governance, security, compliance, or competitive monitoring.
- **Topic concentration** shows where the collected intelligence is strongest.
"""
        )

    st.divider()

    show_latest_news(clean_df)

    st.divider()

    show_competitor_activities(clean_df)

    st.divider()

    show_emerging_technologies(clean_df)

    st.divider()

    show_company_announcements(clean_df)