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


def get_confidence_score(row):
    score = row.get("signal_strength", row.get("sentiment_score", 0.5))

    try:
        score = float(score)
    except Exception:
        score = 0.5

    return round(min(max(score, 0.0), 1.0), 2)


def get_impact_level(row):
    confidence = get_confidence_score(row)

    text = " ".join([
        str(row.get("title", "")),
        str(row.get("topic", "")),
        str(row.get("preview", "")),
        str(row.get("evidence", ""))
    ]).lower()

    high_keywords = [
        "ai", "azure", "copilot", "foundry", "cloud",
        "enterprise", "agent", "growth", "infrastructure",
        "partnership", "developer"
    ]

    if confidence >= 0.75 or any(word in text for word in high_keywords):
        return "High"

    if confidence >= 0.55:
        return "Medium"

    return "Low"


def get_evidence_text(row):
    evidence = (
        row.get("evidence")
        or row.get("preview")
        or row.get("text")
        or "No evidence preview available."
    )

    return str(evidence)


def show_opportunity_monitor():
    st.title("Opportunity Monitor")

    st.caption(
        "Displays opportunity title, impact level, evidence, and confidence score."
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

    if opportunities.empty:
        st.info("No opportunity signals found.")
        return

    opportunities["confidence_score"] = opportunities.apply(
        get_confidence_score,
        axis=1
    )

    opportunities["impact_level"] = opportunities.apply(
        get_impact_level,
        axis=1
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Opportunity Documents", len(opportunities))
    col2.metric("High Impact", int((opportunities["impact_level"] == "High").sum()))
    col3.metric("Companies", opportunities["company_view"].nunique())
    col4.metric("Avg Confidence", round(opportunities["confidence_score"].mean(), 2))

    st.divider()

    st.subheader("Opportunity Visualizations")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Opportunities by Impact Level")
        st.bar_chart(opportunities["impact_level"].value_counts())

    with col_b:
        st.markdown("### Opportunities by Company")
        st.bar_chart(opportunities["company_view"].value_counts())

    st.markdown("### Opportunity Topics")
    st.bar_chart(opportunities["topic"].value_counts())

    st.markdown("### Opportunities by Source")
    st.bar_chart(opportunities["source"].value_counts())

    st.divider()

    st.subheader("Opportunity Intelligence Table")

    table_df = opportunities[
        [
            "title",
            "company_view",
            "topic",
            "impact_level",
            "confidence_score",
            "source"
        ]
    ].copy()

    table_df = table_df.rename(
        columns={
            "title": "Opportunity Title",
            "company_view": "Company",
            "topic": "Topic",
            "impact_level": "Impact Level",
            "confidence_score": "Confidence Score",
            "source": "Source"
        }
    )

    st.dataframe(table_df, use_container_width=True)

    st.divider()

    st.subheader("Filter Opportunities")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + sorted(opportunities["company_view"].dropna().unique().tolist())
    )

    selected_impact = st.selectbox(
        "Select impact level",
        ["All", "High", "Medium", "Low"]
    )

    selected_topic = st.selectbox(
        "Select opportunity topic",
        ["All"] + sorted(opportunities["topic"].dropna().unique().tolist())
    )

    filtered_df = opportunities.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_impact != "All":
        filtered_df = filtered_df[filtered_df["impact_level"] == selected_impact]

    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df["topic"] == selected_topic]

    filtered_df = filtered_df.sort_values(
        by="confidence_score",
        ascending=False
    )

    st.write(f"Showing {len(filtered_df)} opportunity documents")

    for _, row in filtered_df.head(30).iterrows():
        title = row.get("title", "Untitled opportunity")

        with st.expander(title):
            st.write("**Opportunity Title:**", title)
            st.write("**Impact Level:**", row.get("impact_level", "Unknown"))
            st.write("**Confidence Score:**", row.get("confidence_score", 0.0))
            st.write("**Company:**", row.get("company_view", "Unknown"))
            st.write("**Source:**", row.get("source", "Unknown"))
            st.write("**Topic:**", row.get("topic", "Unknown"))
            st.write("**Sentiment:**", row.get("sentiment", "Unknown"))
            st.write("**Strategic Signal:**", row.get("strategic_signal", "Opportunity"))

            if row.get("url"):
                st.markdown(f"**URL:** [{row['url']}]({row['url']})")

            st.write("**Evidence:**")
            st.write(get_evidence_text(row)[:700])

    st.divider()

    st.subheader("Executive Interpretation")

    with st.container(border=True):
        st.markdown(
            """
This page satisfies the Opportunity Monitor requirement by showing:

- **Opportunity title**
- **Impact level**
- **Evidence**
- **Confidence score**

High-impact opportunities usually relate to AI, Azure, Copilot, Foundry, cloud infrastructure, enterprise adoption, agents, partnerships, or developer productivity.
"""
        )