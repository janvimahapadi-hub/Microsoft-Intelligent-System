import pandas as pd
import streamlit as st

from intelligence.recommendation_engine import get_strategic_recommendations


def show_recommendation_card(recommendation):
    title = recommendation.get("recommendation", "Untitled recommendation")
    theme = recommendation.get("theme", "General Opportunity")
    priority = recommendation.get("priority", "Unknown")
    confidence = recommendation.get("confidence", 0.0)
    risk_level = recommendation.get("risk_level", "Unknown")

    with st.expander(f"{priority} Priority: {title}"):
        col1, col2, col3 = st.columns(3)

        col1.metric("Theme", theme)
        col2.metric("Confidence", confidence)
        col3.metric("Risk Level", risk_level)

        st.write("**Expected Impact:**")
        st.write(recommendation.get("expected_impact", "Not available."))

        st.write("**Risk Assessment:**")
        st.write(recommendation.get("risk_assessment", "Not available."))

        st.write("**Execution Plan:**")
        for step in recommendation.get("execution_plan", []):
            st.markdown(f"- {step}")

        st.write("**Recommended Owners:**")
        owners = recommendation.get("owners", [])
        if owners:
            st.write(", ".join(owners))
        else:
            st.write("No owners assigned.")

        st.write("**Success KPIs:**")
        for kpi in recommendation.get("kpis", []):
            st.markdown(f"- {kpi}")

        st.write("**Sentiment Context:**")
        st.write(
            f"Average sentiment score for this topic: {recommendation.get('sentiment_average', 0.0)}"
        )

        st.write("**Supporting Evidence:**")
        for evidence in recommendation.get("evidence", []):
            evidence_title = evidence.get("title", "Evidence")
            evidence_source = evidence.get("source", "Unknown source")
            evidence_url = evidence.get("url", "")
            evidence_summary = evidence.get("summary", "")

            if evidence_url:
                st.markdown(f"- [{evidence_title}]({evidence_url}) - {evidence_source}")
            else:
                st.markdown(f"- {evidence_title} - {evidence_source}")

            if evidence_summary:
                st.caption(evidence_summary)

        related_risks = recommendation.get("related_risks", [])

        if related_risks:
            st.write("**Related Risks:**")
            for risk in related_risks:
                st.markdown(
                    f"- {risk.get('severity_level', 'Unknown')} severity: "
                    f"{risk.get('risk_category', 'Risk')} - "
                    f"{risk.get('risk_title', 'Untitled risk')}"
                )


def show_recommendations():
    st.title("Strategic Recommendations")
    st.caption(
        "Converts opportunities, risks, sentiment, and evidence into prioritized strategic actions."
    )

    topic = st.text_input(
        "Focus topic",
        value="AI Copilot security",
        help="Try Windows, Azure, GitHub, Copilot, Microsoft 365, Xbox, security, regulation, or partners."
    )

    limit = st.slider(
        "Number of recommendations",
        min_value=3,
        max_value=8,
        value=5
    )

    data = get_strategic_recommendations(
        topic=topic,
        limit=limit
    )

    recommendations = data["recommendations"]

    st.subheader("Recommendation Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Recommendations",
        data["total_recommendations"]
    )

    col2.metric(
        "Average Confidence",
        data["average_confidence"]
    )

    col3.metric(
        "High Priority",
        data["priority_counter"].get("High", 0)
    )

    col4.metric(
        "High Risk",
        data["risk_counter"].get("High", 0)
    )

    st.divider()

    st.subheader("Recommendation Portfolio")

    if recommendations:
        table_rows = []

        for recommendation in recommendations:
            table_rows.append({
                "Recommendation": recommendation.get("recommendation", ""),
                "Theme": recommendation.get("theme", ""),
                "Priority": recommendation.get("priority", ""),
                "Risk Level": recommendation.get("risk_level", ""),
                "Confidence": recommendation.get("confidence", 0.0),
                "Sentiment": recommendation.get("sentiment_average", 0.0)
            })

        recommendation_df = pd.DataFrame(table_rows)

        st.dataframe(
            recommendation_df,
            use_container_width=True
        )
    else:
        st.warning("No recommendations found for this topic.")
        return

    st.divider()

    st.subheader("Priority Distribution")

    if data["priority_counter"]:
        priority_df = pd.DataFrame(
            data["priority_counter"].items(),
            columns=["Priority", "Count"]
        )

        st.bar_chart(
            priority_df.set_index("Priority")
        )

    st.divider()

    st.subheader("Risk Distribution")

    if data["risk_counter"]:
        risk_df = pd.DataFrame(
            data["risk_counter"].items(),
            columns=["Risk Level", "Count"]
        )

        st.bar_chart(
            risk_df.set_index("Risk Level")
        )

    st.divider()

    st.subheader("Recommendation Details")

    for recommendation in recommendations:
        show_recommendation_card(recommendation)

    st.divider()

    st.subheader("Interpretation Note")

    st.info(
        "Strategic recommendations are generated through a deterministic decision layer that combines opportunity signals, risk signals, sentiment, and evidence. "
        "The CEO Briefing page can then be used to discuss any recommendation through the local LLM and follow-up Q&A."
    )