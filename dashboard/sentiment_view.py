import pandas as pd
import streamlit as st

from sentiment.sentiment_analyzer import (
    get_sentiment_analysis,
    get_sentiment_trend
)


def show_sentiment_document_card(item):
    title = item.get("title", "Untitled document")
    source = item.get("source", "Unknown source")
    source_group = item.get("source_group", "Other")
    published = item.get("published", "Unknown date")
    url = item.get("url", "")
    label = item.get("sentiment_label", "Neutral")
    score = item.get("sentiment_score", 0.0)
    positive_terms = item.get("positive_terms", 0)
    negative_terms = item.get("negative_terms", 0)
    text = item.get("text", "")

    with st.expander(f"{label} ({score}): {title}"):
        col1, col2, col3 = st.columns(3)

        col1.metric("Sentiment", label)
        col2.metric("Score", score)
        col3.metric("Source Group", source_group)

        st.write("**Source:**", source)
        st.write("**Published:**", published)
        st.write("**Positive Terms:**", positive_terms)
        st.write("**Negative Terms:**", negative_terms)

        if url:
            st.markdown(f"**URL:** [{url}]({url})")

        st.write("**Preview:**")
        st.write(text[:700] if text else "No preview available.")


def show_sentiment_view():
    st.title("Sentiment Analysis")
    st.caption(
        "Analyzes public, news, and official sentiment signals from the collected document repository."
    )

    topic = st.text_input(
        "Focus topic",
        value="AI Copilot security",
        help="Try Reddit, Copilot, Windows, Azure, GitHub, security, regulation, Xbox, or Microsoft 365."
    )

    limit = st.slider(
        "Number of documents to analyze",
        min_value=20,
        max_value=120,
        value=80
    )

    sentiment_data = get_sentiment_analysis(
        topic=topic,
        limit=limit
    )

    documents = sentiment_data["documents"]

    st.subheader("Sentiment Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Documents Analyzed",
        sentiment_data["total_documents"]
    )

    col2.metric(
        "Overall Sentiment Score",
        sentiment_data["overall_average"]
    )

    col3.metric(
        "Positive",
        sentiment_data["label_counter"].get("Positive", 0)
    )

    col4.metric(
        "Negative",
        sentiment_data["label_counter"].get("Negative", 0)
    )

    st.divider()

    st.subheader("Sentiment Distribution")

    if sentiment_data["label_counter"]:
        label_df = pd.DataFrame(
            sentiment_data["label_counter"].items(),
            columns=["Sentiment Label", "Count"]
        )

        st.dataframe(
            label_df,
            use_container_width=True
        )

        st.bar_chart(
            label_df.set_index("Sentiment Label")
        )
    else:
        st.warning("No sentiment labels available.")

    st.divider()

    st.subheader("Sentiment by Source Group")

    if sentiment_data["average_by_source_group"]:
        source_group_df = pd.DataFrame(
            sentiment_data["average_by_source_group"].items(),
            columns=["Source Group", "Average Sentiment"]
        ).sort_values(
            by="Average Sentiment",
            ascending=False
        )

        st.dataframe(
            source_group_df,
            use_container_width=True
        )

        st.bar_chart(
            source_group_df.set_index("Source Group")
        )

        if "Public / Community" not in sentiment_data["average_by_source_group"]:
            st.info(
                "No public/community sentiment was found for this topic. "
                "Try a broader topic such as Microsoft, AI, Copilot, or Reddit."
            )
    else:
        st.warning("No source group sentiment available.")

    st.divider()

    st.subheader("Sentiment Trend")

    trend_rows = get_sentiment_trend(
        topic=topic,
        limit=limit
    )

    if trend_rows:
        trend_df = pd.DataFrame(trend_rows)

        st.dataframe(
            trend_df,
            use_container_width=True
        )

        st.line_chart(
            trend_df.set_index("Date")["Average Sentiment"]
        )
    else:
        st.info(
            "No dated documents were available for trend analysis."
        )

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "Most Positive",
            "Most Negative",
            "Public / Community"
        ]
    )

    with tab1:
        positive_docs = [
            item for item in documents
            if item["sentiment_label"] == "Positive"
        ]

        positive_docs = sorted(
            positive_docs,
            key=lambda x: x["sentiment_score"],
            reverse=True
        )

        if positive_docs:
            for item in positive_docs[:10]:
                show_sentiment_document_card(item)
        else:
            st.warning("No positive documents found for this topic.")

    with tab2:
        negative_docs = [
            item for item in documents
            if item["sentiment_label"] == "Negative"
        ]

        negative_docs = sorted(
            negative_docs,
            key=lambda x: x["sentiment_score"]
        )

        if negative_docs:
            for item in negative_docs[:10]:
                show_sentiment_document_card(item)
        else:
            st.warning("No negative documents found for this topic.")

    with tab3:
        public_docs = [
            item for item in documents
            if item["source_group"] == "Public / Community"
        ]

        if public_docs:
            for item in public_docs[:10]:
                show_sentiment_document_card(item)
        else:
            st.warning(
                "No public/community documents found for this topic. "
                "Try a broader topic or check whether Reddit data exists in raw_documents.json."
            )

    st.divider()

    st.subheader("Interpretation Note")

    st.info(
        "This sentiment module uses transparent lexicon-based scoring. "
        "It is designed as a lightweight public perception signal, not as the final decision-maker. "
        "Strategic recommendations should combine sentiment with retrieved evidence, risk analysis, opportunity analysis, and CEO reasoning."
    )