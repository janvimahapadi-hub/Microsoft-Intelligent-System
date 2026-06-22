import pandas as pd
import streamlit as st

from intelligence.market_analyzer import (
    get_market_intelligence,
    get_documents_by_signal
)


def show_document_card(document):
    title = document.get("title", "Untitled document")
    source = document.get("source", "Unknown source")
    source_type = document.get("source_type", "unknown")
    published = document.get("published", "Unknown date")
    url = document.get("url", "")
    text = document.get("text", "")
    signal_types = document.get("signal_types", [])

    with st.expander(title):
        st.write("**Source:**", source)
        st.write("**Source Type:**", source_type)
        st.write("**Published:**", published)
        st.write("**Signals:**", ", ".join(signal_types))

        if url:
            st.markdown(f"**URL:** [{url}]({url})")

        st.write("**Preview:**")
        st.write(text[:700] if text else "No preview available.")


def show_signal_section(title, signal_name, topic):
    st.subheader(title)

    documents = get_documents_by_signal(
        signal_name=signal_name,
        topic=topic,
        limit=5
    )

    if not documents:
        st.warning(f"No documents found for {signal_name}.")
        return

    for document in documents:
        show_document_card(document)


def show_market_intelligence():
    st.title("Market Intelligence")
    st.caption(
        "Market signals extracted from collected public sources."
    )

    topic = st.text_input(
        "Focus topic",
        value="AI Copilot cloud security",
        help="Try topics such as Windows, Xbox, Copilot, Azure, security, GitHub, or regulation."
    )

    result_limit = st.slider(
        "Number of market signals to analyze",
        min_value=5,
        max_value=30,
        value=15
    )

    market_data = get_market_intelligence(
        topic=topic,
        limit=result_limit
    )

    st.subheader("Market Intelligence Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Relevant Signals",
        market_data["total_results"]
    )

    col2.metric(
        "Signal Categories",
        len(market_data["signal_counter"])
    )

    col3.metric(
        "Sources Represented",
        len(market_data["source_counter"])
    )

    st.divider()

    st.subheader("Signal Distribution")

    if market_data["signal_counter"]:
        signal_df = pd.DataFrame(
            market_data["signal_counter"].items(),
            columns=["Signal Type", "Count"]
        ).sort_values(
            by="Count",
            ascending=False
        )

        st.dataframe(
            signal_df,
            use_container_width=True
        )

        st.bar_chart(
            signal_df.set_index("Signal Type")
        )
    else:
        st.warning("No signal distribution available.")

    st.divider()

    st.subheader("Sources Represented")

    if market_data["source_counter"]:
        source_df = pd.DataFrame(
            market_data["source_counter"].items(),
            columns=["Source", "Count"]
        ).sort_values(
            by="Count",
            ascending=False
        )

        st.dataframe(
            source_df,
            use_container_width=True
        )
    else:
        st.warning("No source distribution available.")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Recent Market Signals",
            "Company Announcements",
            "Competitor Activity",
            "Emerging Technologies"
        ]
    )

    with tab1:
        st.subheader("Recent / Relevant Market Signals")

        if not market_data["documents"]:
            st.warning("No relevant documents found for this topic.")
        else:
            for document in market_data["documents"]:
                show_document_card(document)

    with tab2:
        show_signal_section(
            title="Important Company Announcements",
            signal_name="Company Announcement",
            topic=topic
        )

    with tab3:
        show_signal_section(
            title="Competitor Activities",
            signal_name="Competitor Activity",
            topic=topic
        )

        st.info(
            "If competitor activity is limited, add more competitor sources such as AWS, Google Cloud, NVIDIA, Salesforce, or Apple. "
            "The current view only reflects the sources already collected."
        )

    with tab4:
        show_signal_section(
            title="Emerging Technologies",
            signal_name="Emerging Technology",
            topic=topic
        )

    st.divider()

    st.subheader("Interpretation Note")

    st.info(
        "This page uses rule-based market signal classification over the collected document repository. "
        "It is designed to provide transparent market intelligence signals before the CEO briefing stage."
    )