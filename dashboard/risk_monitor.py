import pandas as pd
import streamlit as st

from intelligence.risk_analyzer import get_risk_summary


def show_risk_card(risk):
    title = risk.get("risk_title", "Untitled risk")
    category = risk.get("risk_category", "General Strategic Risk")
    severity = risk.get("severity_level", "Unknown")
    confidence = risk.get("confidence", 0.0)
    source = risk.get("source", "Unknown source")
    source_type = risk.get("source_type", "unknown")
    published = risk.get("published", "Unknown date")
    url = risk.get("url", "")
    mitigation = risk.get("mitigation", "")
    evidence = risk.get("evidence", "")

    with st.expander(f"{severity} Severity: {category} | {title}"):
        col1, col2, col3 = st.columns(3)

        col1.metric("Severity Level", severity)
        col2.metric("Confidence", confidence)
        col3.metric("Risk Score", risk.get("score", 0))

        st.write("**Risk Mitigation:**")
        st.write(mitigation)

        st.write("**Source:**", source)
        st.write("**Source Type:**", source_type)
        st.write("**Published:**", published)

        if url:
            st.markdown(f"**URL:** [{url}]({url})")

        st.write("**Evidence:**")
        st.write(evidence if evidence else "No evidence preview available.")


def show_risk_monitor():
    st.title("Risk Monitor")
    st.caption(
        "Identifies potential strategic, security, regulatory, competitive, and operational risks."
    )

    topic = st.text_input(
        "Focus topic",
        value="AI Copilot cloud security",
        help="Try Windows, Xbox, GitHub, Azure, Copilot, security, regulation, partners, or Microsoft 365."
    )

    limit = st.slider(
        "Number of risks to display",
        min_value=5,
        max_value=25,
        value=10
    )

    summary = get_risk_summary(
        topic=topic,
        limit=limit
    )

    risks = summary["risks"]

    st.subheader("Risk Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Risks Found",
        summary["total_risks"]
    )

    high_count = summary["severity_counter"].get("High", 0)
    medium_count = summary["severity_counter"].get("Medium", 0)

    col2.metric(
        "High Severity",
        high_count
    )

    col3.metric(
        "Medium Severity",
        medium_count
    )

    st.divider()

    st.subheader("Severity Distribution")

    if summary["severity_counter"]:
        severity_df = pd.DataFrame(
            summary["severity_counter"].items(),
            columns=["Severity Level", "Count"]
        )

        st.dataframe(
            severity_df,
            use_container_width=True
        )

        st.bar_chart(
            severity_df.set_index("Severity Level")
        )
    else:
        st.warning("No severity distribution available.")

    st.divider()

    st.subheader("Risk Categories")

    if summary["category_counter"]:
        category_df = pd.DataFrame(
            summary["category_counter"].items(),
            columns=["Risk Category", "Count"]
        ).sort_values(
            by="Count",
            ascending=False
        )

        st.dataframe(
            category_df,
            use_container_width=True
        )

        st.bar_chart(
            category_df.set_index("Risk Category")
        )
    else:
        st.warning("No risk categories available.")

    st.divider()

    st.subheader("Risk Details")

    if not risks:
        st.warning(
            "No risks found for this topic. Try a broader topic such as AI, Azure, Windows, GitHub, security, privacy, or regulation."
        )
        return

    for risk in risks:
        show_risk_card(risk)

    st.divider()

    st.subheader("Interpretation Note")

    st.info(
        "Risk detection uses transparent keyword and category-based scoring. "
        "Severity is based on risk-related terms, category strength, and supporting metadata. "
        "This page is designed as an explainable early-warning layer before deeper CEO-level reasoning."
    )