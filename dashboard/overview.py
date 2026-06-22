import json
from pathlib import Path

import pandas as pd
import streamlit as st


RAW_PATH = Path("data/raw_documents.json")
CLEANED_PATH = Path("data/cleaned_documents.json")
SENTIMENT_PATH = Path("data/sentiment_results.json")


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
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


def show_overview():
    st.title("Project Overview")
    st.caption(
        "AI-powered Strategic Intelligence Platform for executive decision support."
    )

    st.subheader("Problem Statement")

    st.write(
        "Technology leaders receive hundreds of updates from AI announcements, cloud releases, "
        "security reports, developer communities, market signals, partner ecosystems, and competitor activity. "
        "Manually analyzing all this information is slow, repetitive, and can cause important opportunities or risks to be missed."
    )

    st.write(
        "This project transforms large volumes of unstructured text into executive-level intelligence "
        "that supports faster, evidence-based strategic decision-making."
    )

    st.divider()

    st.subheader("Project Goal")

    st.markdown(
        """
Build an AI-powered Strategic Intelligence Platform that can:

- Collect information from Microsoft and competitor sources
- Clean and prepare unstructured text data
- Identify opportunities and risks
- Measure sentiment and market signals
- Compare Microsoft with AWS, Google Cloud, OpenAI, and NVIDIA
- Retrieve relevant evidence for strategic questions
- Generate CEO-level briefings using a local LLM
- Produce actionable recommendations with KPIs and risks
"""
    )

    st.divider()

    raw_data = load_json(RAW_PATH)
    cleaned_data = load_json(CLEANED_PATH)
    sentiment_data = load_json(SENTIMENT_PATH)

    df = pd.DataFrame(sentiment_data) if sentiment_data else pd.DataFrame()

    documents_collected = len(raw_data)
    cleaned_documents = len(cleaned_data)
    sentiment_coverage = len(df)

    if not df.empty:
        df["company_view"] = df.apply(get_company, axis=1)

    topics_detected = df["topic"].nunique() if not df.empty and "topic" in df else 0
    opportunities = int((df["strategic_signal"] == "Opportunity").sum()) if not df.empty and "strategic_signal" in df else 0
    risks = int((df["strategic_signal"] == "Risk").sum()) if not df.empty and "strategic_signal" in df else 0
    companies_tracked = df["company_view"].nunique() if not df.empty and "company_view" in df else 0

    microsoft_docs = int((df["company_view"] == "Microsoft").sum()) if not df.empty and "company_view" in df else 0
    competitor_docs = sentiment_coverage - microsoft_docs

    st.subheader("Executive Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Documents Collected", documents_collected)
    col2.metric("Cleaned Documents", cleaned_documents)
    col3.metric("Sentiment Coverage", sentiment_coverage)

    col4, col5, col6 = st.columns(3)
    col4.metric("Companies Tracked", companies_tracked)
    col5.metric("Microsoft Docs", microsoft_docs)
    col6.metric("Competitor Docs", competitor_docs)

    col7, col8, col9 = st.columns(3)
    col7.metric("Topics Detected", topics_detected)
    col8.metric("Opportunities Found", opportunities)
    col9.metric("Risks Found", risks)

    st.divider()

    if not df.empty and "company_view" in df:
        st.subheader("Company Coverage")

        company_counts = df["company_view"].value_counts()
        st.bar_chart(company_counts)

        top_company = company_counts.idxmax()
        st.info(
            f"The largest intelligence coverage currently comes from **{top_company}**. "
            "Adding more balanced competitor sources can improve strategic comparison quality."
        )

    st.divider()

    st.subheader("System Workflow")

    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;
            node [shape=box, style="rounded,filled", color="#2563eb", fillcolor="#eff6ff", fontname="Arial"];

            A [label="Data Collection"];
            B [label="Cleaning"];
            C [label="Chunking"];
            D [label="Hybrid Retrieval"];
            E [label="Local LLM Reasoning"];
            F [label="CEO Briefing"];
            G [label="Sentiment & Signals"];
            H [label="Competitor Intelligence"];
            I [label="Recommendations"];

            A -> B -> C -> D -> E -> F;
            B -> G -> I;
            G -> H;
            D -> I;
            H -> I;
        }
        """
    )

    st.divider()

    st.subheader("Dashboard Capabilities")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
### 🧠 CEO Briefing
Ask strategic questions and generate evidence-based executive briefings with actions, risks, KPIs, and evidence.
"""
        )

        st.markdown(
            """
### 🚀 Opportunity Monitor
Tracks high-value opportunity signals such as AI adoption, Azure growth, Copilot, Foundry, and partner ecosystem expansion.
"""
        )

    with c2:
        st.markdown(
            """
### 📈 Sentiment Intelligence
Analyzes documents for positive and negative sentiment, topic categories, and strategic business signals.
"""
        )

        st.markdown(
            """
### ⚠️ Risk Monitor
Identifies risk signals related to cybersecurity, governance, compliance, competition, privacy, and operational challenges.
"""
        )

    with c3:
        st.markdown(
            """
### 🏁 Competitor Intelligence
Compares Microsoft-related intelligence with AWS, Google Cloud, OpenAI, NVIDIA, and other competitor signals.
"""
        )

        st.markdown(
            """
### ✅ Recommendations
Converts evidence, sentiment, opportunities, risks, and competitor activity into executive-level recommendations.
"""
        )

    st.divider()

    st.subheader("Business Value")

    st.markdown(
        """
This system helps leadership teams by providing:

- Faster decision-making
- Reduced information overload
- Early risk detection
- Opportunity identification
- Competitor comparison
- Evidence-backed recommendations
- Continuous strategic monitoring
- Clear next-step actions for leadership
"""
    )

    st.divider()

    st.subheader("Future Scope")

    st.markdown(
        """
Future improvements can include:

- More competitor sources from Anthropic, Meta, IBM, Oracle, and Salesforce
- Real-time news and RSS monitoring
- Hybrid retrieval tuning with source weighting
- Multi-company benchmarking
- Trend forecasting over time
- PDF export for executive reports
- Automated weekly intelligence briefings
"""
    )