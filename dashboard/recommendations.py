import json

import pandas as pd
import streamlit as st

from intelligence.ceo_briefing import CEOBriefing


SENTIMENT_PATH = "data/sentiment_results.json"


@st.cache_resource
def get_briefing_engine():
    return CEOBriefing(company_name="Microsoft")


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


def show_recommendations():
    st.title("Executive Recommendations")
    st.caption(
        "Question-specific recommendations plus global strategy recommendations from Microsoft and competitor intelligence."
    )

    st.subheader("Ask a Strategic Question")

    question = st.text_area(
        "Strategic Question",
        value="How should Microsoft compete with AWS and Google Cloud in AI infrastructure?",
        height=110
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        top_k = st.slider(
            "Evidence chunks",
            min_value=3,
            max_value=8,
            value=5
        )

    with col2:
        mode_label = st.radio(
            "Recommendation mode",
            ["Fast Recommendation", "Deep Recommendation"],
            horizontal=True
        )

    mode = "fast" if mode_label == "Fast Recommendation" else "playbook"

    if st.button("Generate Recommendations"):
        if not question.strip():
            st.warning("Please enter a strategic question.")
            return

        with st.spinner("Generating question-specific recommendations..."):
            try:
                briefing_engine = get_briefing_engine()

                report = briefing_engine.generate(
                    strategic_question=question,
                    top_k=top_k,
                    mode=mode
                )

                st.session_state["recommendation_report"] = report

                st.success("Recommendations generated successfully.")

            except Exception as error:
                st.error(f"Could not generate recommendations: {error}")

    if "recommendation_report" in st.session_state:
        report = st.session_state["recommendation_report"]

        st.subheader("Question-Specific Recommendations")
        st.markdown(report["briefing"])

        confidence = report.get("retrieval_confidence", 0.0)

        st.metric("Retrieval Confidence", f"{confidence:.2f}")
        st.progress(min(confidence, 1.0))

        st.subheader("Evidence Used")

        for item in report.get("evidence", []):
            company = (
                item.get("company")
                or item.get("competitor")
                or item.get("source", "Unknown")
            )

            with st.expander(item.get("title", "Evidence")):
                st.write("**Company/Source:**", company)
                st.write("**Source:**", item.get("source", "Unknown"))
                st.write("**Source Type:**", item.get("source_type", "Unknown"))

                if item.get("url"):
                    st.markdown(f"**URL:** [{item['url']}]({item['url']})")

                st.write("**Evidence Preview:**")
                st.write(item.get("evidence", "")[:700])

    st.divider()

    st.subheader("Global Executive Recommendations")

    data = load_data()
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No sentiment data found.")
        return

    if "strategic_signal" not in df.columns:
        st.warning("Run strategic_classifier.py first.")
        return

    df["company_view"] = df.apply(get_company, axis=1)
    clean_df = df[df["strategic_signal"] != "Irrelevant"].copy()

    opportunities = clean_df[clean_df["strategic_signal"] == "Opportunity"]
    risks = clean_df[clean_df["strategic_signal"] == "Risk"]

    top_topics = (
        clean_df["topic"]
        .value_counts()
        .head(3)
        .index
        .tolist()
    )

    company_counts = clean_df["company_view"].value_counts()
    most_covered_company = company_counts.idxmax() if not company_counts.empty else "Unknown"

    competitor_df = clean_df[clean_df["company_view"] != "Microsoft"]
    competitor_count = len(competitor_df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Opportunity Signals", len(opportunities))
    c2.metric("Risk Signals", len(risks))
    c3.metric("Competitor Docs", competitor_count)
    c4.metric("Top Covered Company", most_covered_company)

    st.markdown(
        f"""
### Recommended CEO Priorities

#### 1. Defend and expand Microsoft’s AI infrastructure position
- **Why:** Current intelligence includes competitor activity from AWS, Google Cloud, OpenAI, and NVIDIA.
- **Action:** Strengthen Azure AI infrastructure, model hosting, enterprise governance, and cost-performance positioning.
- **KPIs:** Azure AI workload growth, enterprise AI adoption rate, customer retention, inference cost efficiency.

#### 2. Scale high-value Microsoft AI opportunities
- **Why:** The system detected **{len(opportunities)} opportunity signals** across topics such as **{", ".join(top_topics)}**.
- **Action:** Prioritize Copilot, Microsoft Foundry, Azure AI, agentic AI, and partner-led enterprise adoption.
- **KPIs:** Copilot usage, Foundry deployments, partner-led pipeline, production AI workloads.

#### 3. Strengthen AI security and governance
- **Why:** The system detected **{len(risks)} risk signals**, including security, governance, compliance, and competitive threats.
- **Action:** Embed security, compliance, evaluation, and governance controls into AI deployment workflows.
- **KPIs:** incident reduction, governance coverage, compliance review completion, secure deployment rate.

#### 4. Monitor competitor momentum continuously
- **Why:** Competitor evidence can reveal market direction earlier than internal sources alone.
- **Action:** Track AWS, Google Cloud, OpenAI, NVIDIA, and future sources such as Anthropic, Meta, IBM, Oracle, and Salesforce.
- **KPIs:** competitor source coverage, source freshness, competitor opportunity/risk ratio, response time to market moves.
"""
    )

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top Opportunity Evidence")

        top_opportunities = opportunities.sort_values(
            by="sentiment_score",
            ascending=False
        ).head(5)

        for _, row in top_opportunities.iterrows():
            with st.expander(row["title"]):
                st.write("**Company:**", row["company_view"])
                st.write("**Source:**", row["source"])
                st.write("**Topic:**", row["topic"])
                st.write("**Sentiment:**", row["sentiment"])

                if row.get("url"):
                    st.markdown(f"**URL:** [{row['url']}]({row['url']})")

                st.write(row.get("preview", ""))

    with col_b:
        st.subheader("Top Risk Evidence")

        top_risks = risks.sort_values(
            by="sentiment_score",
            ascending=False
        ).head(5)

        for _, row in top_risks.iterrows():
            with st.expander(row["title"]):
                st.write("**Company:**", row["company_view"])
                st.write("**Source:**", row["source"])
                st.write("**Topic:**", row["topic"])
                st.write("**Sentiment:**", row["sentiment"])

                if row.get("url"):
                    st.markdown(f"**URL:** [{row['url']}]({row['url']})")

                st.write(row.get("preview", ""))

    st.divider()

    st.subheader("Recommended Next CEO Questions")

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
            <ul>
                <li style="color:#0f172a;">How should Microsoft defend Azure against AWS and Google Cloud?</li>
                <li style="color:#0f172a;">Which competitor poses the largest threat in enterprise AI?</li>
                <li style="color:#0f172a;">Which AI opportunity has the strongest customer impact?</li>
                <li style="color:#0f172a;">Which security or governance risk could block enterprise AI adoption?</li>
                <li style="color:#0f172a;">What 90-day roadmap should Microsoft execute first?</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )