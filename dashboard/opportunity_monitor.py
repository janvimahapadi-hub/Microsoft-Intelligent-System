import pandas as pd
import streamlit as st

from intelligence.opportunity_analyzer import get_opportunity_summary


def show_opportunity_card(opportunity):
    title = opportunity.get("opportunity_title", "Untitled opportunity")
    theme = opportunity.get("title", "General Opportunity")
    impact = opportunity.get("impact_level", "Unknown")
    confidence = opportunity.get("confidence", 0.0)
    source = opportunity.get("source", "Unknown source")
    source_type = opportunity.get("source_type", "unknown")
    published = opportunity.get("published", "Unknown date")
    url = opportunity.get("url", "")
    rationale = opportunity.get("strategic_rationale", "")
    evidence = opportunity.get("evidence", "")

    with st.expander(f"{theme}: {title}"):
        col1, col2, col3 = st.columns(3)

        col1.metric("Impact Level", impact)
        col2.metric("Confidence", confidence)
        col3.metric("Opportunity Score", opportunity.get("score", 0))

        st.write("**Strategic Rationale:**")
        st.write(rationale)

        st.write("**Source:**", source)
        st.write("**Source Type:**", source_type)
        st.write("**Published:**", published)

        if url:
            st.markdown(f"**URL:** [{url}]({url})")

        st.write("**Evidence:**")
        st.write(evidence if evidence else "No evidence preview available.")


def show_opportunity_monitor():
    st.title("Opportunity Monitor")
    st.caption(
        "Identifies potential strategic opportunities from collected public information."
    )

    topic = st.text_input(
        "Focus topic",
        value="AI Copilot cloud security",
        help="Try Windows, Xbox, GitHub, Azure, Copilot, security, partners, or Microsoft 365."
    )

    limit = st.slider(
        "Number of opportunities to display",
        min_value=5,
        max_value=25,
        value=10
    )

    summary = get_opportunity_summary(
        topic=topic,
        limit=limit
    )

    opportunities = summary["opportunities"]

    st.subheader("Opportunity Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Opportunities Found",
        summary["total_opportunities"]
    )

    high_count = summary["impact_counter"].get("High", 0)
    medium_count = summary["impact_counter"].get("Medium", 0)

    col2.metric(
        "High Impact",
        high_count
    )

    col3.metric(
        "Medium Impact",
        medium_count
    )

    st.divider()

    st.subheader("Impact Distribution")

    if summary["impact_counter"]:
        impact_df = pd.DataFrame(
            summary["impact_counter"].items(),
            columns=["Impact Level", "Count"]
        )

        st.dataframe(
            impact_df,
            use_container_width=True
        )

        st.bar_chart(
            impact_df.set_index("Impact Level")
        )
    else:
        st.warning("No impact distribution available.")

    st.divider()

    st.subheader("Opportunity Themes")

    if summary["theme_counter"]:
        theme_df = pd.DataFrame(
            summary["theme_counter"].items(),
            columns=["Theme", "Count"]
        ).sort_values(
            by="Count",
            ascending=False
        )

        st.dataframe(
            theme_df,
            use_container_width=True
        )

        st.bar_chart(
            theme_df.set_index("Theme")
        )
    else:
        st.warning("No opportunity themes available.")

    st.divider()

    st.subheader("Opportunity Details")

    if not opportunities:
        st.warning(
            "No opportunities found for this topic. Try a broader topic such as AI, Azure, Windows, GitHub, or security."
        )
        return

    for opportunity in opportunities:
        show_opportunity_card(opportunity)

    st.divider()

    st.subheader("Interpretation Note")

    st.info(
        "Opportunity detection uses transparent keyword and theme-based scoring. "
        "This makes the monitor explainable and reliable for dashboard use. "
        "The CEO briefing can then use RAG and the local LLM for deeper reasoning."
    )