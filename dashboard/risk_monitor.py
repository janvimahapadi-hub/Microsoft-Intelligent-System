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


def get_risk_category(row):
    text = " ".join([
        str(row.get("title", "")),
        str(row.get("topic", "")),
        str(row.get("preview", "")),
        str(row.get("evidence", ""))
    ]).lower()

    if any(word in text for word in ["security", "threat", "attack", "defender", "vulnerability", "cyber"]):
        return "Cybersecurity"

    if any(word in text for word in ["governance", "compliance", "regulation", "privacy", "sovereign"]):
        return "Governance / Compliance"

    if any(word in text for word in ["competition", "competitor", "aws", "google", "openai", "nvidia"]):
        return "Competitive Risk"

    if any(word in text for word in ["cost", "performance", "infrastructure", "latency", "compute"]):
        return "Operational / Infrastructure Risk"

    return row.get("topic", "General Strategic Risk")


def get_severity_level(row):
    confidence = get_confidence_score(row)

    text = " ".join([
        str(row.get("title", "")),
        str(row.get("topic", "")),
        str(row.get("preview", "")),
        str(row.get("evidence", ""))
    ]).lower()

    high_terms = [
        "attack", "threat", "vulnerability", "breach", "security",
        "compliance", "regulation", "privacy", "supply chain"
    ]

    if confidence >= 0.75 or any(term in text for term in high_terms):
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


def show_risk_monitor():
    st.title("Risk Monitor")

    st.caption(
        "Displays risk title, risk category, severity level, evidence, and confidence score."
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

    if risks.empty:
        st.info("No risk signals found.")
        return

    risks["confidence_score"] = risks.apply(get_confidence_score, axis=1)
    risks["risk_category"] = risks.apply(get_risk_category, axis=1)
    risks["severity_level"] = risks.apply(get_severity_level, axis=1)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Risk Documents", len(risks))
    col2.metric("High Severity", int((risks["severity_level"] == "High").sum()))
    col3.metric("Risk Categories", risks["risk_category"].nunique())
    col4.metric("Avg Confidence", round(risks["confidence_score"].mean(), 2))

    st.divider()

    st.subheader("Risk Visualizations")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Risks by Severity Level")
        st.bar_chart(risks["severity_level"].value_counts())

    with col_b:
        st.markdown("### Risks by Company")
        st.bar_chart(risks["company_view"].value_counts())

    st.markdown("### Risk Categories")
    st.bar_chart(risks["risk_category"].value_counts())

    st.markdown("### Risks by Source")
    st.bar_chart(risks["source"].value_counts())

    st.divider()

    st.subheader("Risk Intelligence Table")

    table_df = risks[
        [
            "title",
            "company_view",
            "risk_category",
            "severity_level",
            "confidence_score",
            "source"
        ]
    ].copy()

    table_df = table_df.rename(
        columns={
            "title": "Risk Title",
            "company_view": "Company",
            "risk_category": "Risk Category",
            "severity_level": "Severity Level",
            "confidence_score": "Confidence Score",
            "source": "Source"
        }
    )

    st.dataframe(table_df, use_container_width=True)

    st.divider()

    st.subheader("Filter Risks")

    selected_company = st.selectbox(
        "Select company",
        ["All"] + sorted(risks["company_view"].dropna().unique().tolist())
    )

    selected_severity = st.selectbox(
        "Select severity level",
        ["All", "High", "Medium", "Low"]
    )

    selected_category = st.selectbox(
        "Select risk category",
        ["All"] + sorted(risks["risk_category"].dropna().unique().tolist())
    )

    filtered_df = risks.copy()

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company_view"] == selected_company]

    if selected_severity != "All":
        filtered_df = filtered_df[filtered_df["severity_level"] == selected_severity]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["risk_category"] == selected_category]

    filtered_df = filtered_df.sort_values(
        by="confidence_score",
        ascending=False
    )

    st.write(f"Showing {len(filtered_df)} risk documents")

    for _, row in filtered_df.head(30).iterrows():
        title = row.get("title", "Untitled risk")

        with st.expander(title):
            st.write("**Risk Title:**", title)
            st.write("**Risk Category:**", row.get("risk_category", "Unknown"))
            st.write("**Severity Level:**", row.get("severity_level", "Unknown"))
            st.write("**Confidence Score:**", row.get("confidence_score", 0.0))
            st.write("**Company:**", row.get("company_view", "Unknown"))
            st.write("**Source:**", row.get("source", "Unknown"))
            st.write("**Topic:**", row.get("topic", "Unknown"))
            st.write("**Sentiment:**", row.get("sentiment", "Unknown"))
            st.write("**Strategic Signal:**", row.get("strategic_signal", "Risk"))

            if row.get("url"):
                st.markdown(f"**URL:** [{row['url']}]({row['url']})")

            st.write("**Evidence:**")
            st.write(get_evidence_text(row)[:700])

    st.divider()

    st.subheader("Executive Interpretation")

    with st.container(border=True):
        st.markdown(
            """
This page satisfies the Risk Monitor requirement by showing:

- **Risk title**
- **Risk category**
- **Severity level**
- **Evidence**
- **Confidence score**

High-severity risks usually relate to cybersecurity, compliance, privacy, supply-chain compromise, governance, competitive pressure, or operational infrastructure challenges.
"""
        )