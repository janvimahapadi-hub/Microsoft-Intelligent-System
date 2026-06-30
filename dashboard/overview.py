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
    if "anthropic" in source_lower:
        return "Anthropic"

    return "Microsoft"


def show_overview():
    st.title("Project Overview")

    st.caption(
        "AI CEO Strategic Intelligence Agent with RAG, hybrid retrieval, sentiment analysis, "
        "competitor intelligence, validation, memory, and local LLM reasoning."
    )

    st.subheader("Problem Statement")

    st.write(
        "Technology leaders receive large volumes of updates from AI announcements, cloud releases, "
        "security reports, developer communities, partner ecosystems, and competitor activity. "
        "Manually analyzing this information is slow and can cause important opportunities or risks to be missed."
    )

    st.write(
        "This project converts unstructured strategic information into evidence-based executive intelligence "
        "for CEO-level decision support."
    )

    st.divider()

    st.subheader("Project Goal")

    st.markdown(
        """
Build an AI-powered Strategic Intelligence Agent that can:

- Collect Microsoft and competitor intelligence
- Clean and prepare unstructured text
- Classify sentiment, risks, opportunities, and topics
- Retrieve relevant evidence using FAISS + BM25 hybrid retrieval
- Plan before execution using a Planner Agent
- Select tools autonomously using a Tool Agent
- Analyze risks, opportunities, competitors, and market signals
- Validate recommendations before presentation
- Store short-term memory for follow-up questions
- Generate CEO-level briefings using a local LLM through Ollama
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

    st.subheader("System Architecture")

    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;
            node [shape=box, style="rounded,filled", color="#2563eb", fillcolor="#eff6ff", fontname="Arial"];

            A [label="Data Collection"];
            B [label="Cleaning"];
            C [label="Chunking"];
            D [label="Embedding Model\\nall-MiniLM-L6-v2"];
            E [label="FAISS Vector Store"];
            F [label="BM25 Keyword Index"];
            G [label="Hybrid Retriever"];
            H [label="Sentiment + Strategic Signals"];
            I [label="Dashboards"];

            A -> B -> C;
            C -> D -> E;
            C -> F;
            E -> G;
            F -> G;
            B -> H;
            H -> I;
        }
        """
    )

    st.divider()

    st.subheader("Agentic CEO Briefing Workflow")

    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;
            node [shape=box, style="rounded,filled", color="#16a34a", fillcolor="#ecfdf5", fontname="Arial"];

            Goal [label="User Goal"];
            Plan [label="Planner Agent\\nCreates Plan"];
            Tool [label="Tool Agent\\nSelects Tools"];
            Query [label="Dynamic Query Expansion"];
            Retrieve [label="Hybrid Retrieval\\nFAISS + BM25"];
            Analyze [label="Strategic Analysis\\nRisk / Opportunity / Market / Competitor"];
            Validate [label="Validation Agent\\nConfidence + Warnings"];
            Decide [label="Agent Decision"];
            Memory [label="Memory Agent\\nSession Memory"];
            Prompt [label="Prompt Builder"];
            LLM [label="Ollama Local LLM\\nQwen / Llama"];
            Briefing [label="CEO Briefing"];

            Goal -> Plan -> Tool -> Query -> Retrieve -> Analyze -> Validate -> Decide -> Memory -> Prompt -> LLM -> Briefing;
        }
        """
    )

    st.info(
        "This workflow demonstrates explicit agent behaviour: planning before execution, "
        "autonomous tool selection, evidence retrieval, analysis, validation, decision-making, "
        "memory, and final recommendation generation."
    )

    st.divider()

    st.subheader("How This Differs from Simple RAG")

    st.markdown(
        """
A simple RAG system usually follows:

`User Question → Retrieve Evidence → Prompt → LLM → Answer`

This project extends that into an agent workflow:

`Goal → Plan → Select Tools → Retrieve → Analyze → Validate → Decide → Recommend → Memory`

The LLM is not doing all the work. It only generates the final briefing after the agent has planned, retrieved, analyzed, validated, and prepared grounded context.
"""
    )

    st.divider()

    st.subheader("Main Components")

    st.markdown(
        """
### Planner Agent
Creates an execution plan based on the user's strategic question.

### Tool Agent
Selects tools such as hybrid retrieval, risk analysis, opportunity analysis, market intelligence, or competitor intelligence.

### Hybrid Retriever
Uses both FAISS semantic search and BM25 keyword search to retrieve evidence.

### Strategic Analysis
Matches retrieved evidence with `sentiment_results.json` and identifies risks, opportunities, topics, sentiments, competitor signals, and market signals.

### Validation Agent
Checks evidence count, source diversity, company diversity, URLs, confidence, and readiness.

### Memory Agent
Stores the recent interaction during the session so follow-up questions can use previous context.

### Ollama Local LLM
Generates the final CEO briefing using only retrieved evidence and agent analysis.
"""
    )

    st.divider()

    st.subheader("Dashboard Capabilities")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
### 🧠 CEO Briefing
Generates evidence-based strategic briefings with planning, tool selection, validation, risks, KPIs, and evidence.
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
Converts evidence, sentiment, opportunities, risks, competitor activity, and validation results into executive-level recommendations.
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
- Transparent agent workflow
- Validation before recommendation
- Follow-up Q&A with session memory
"""
    )

    st.divider()

    st.subheader("Future Scope")

    st.markdown(
        """
Future improvements can include:

- Persistent memory using SQLite
- More competitor sources from Anthropic, Meta, IBM, Oracle, and Salesforce
- Real-time RSS monitoring
- LangChain or LangGraph integration
- Better query expansion and retrieval tuning
- Multi-company benchmarking
- Trend forecasting over time
- PDF export for executive reports
- Automated weekly intelligence briefings
"""
    )