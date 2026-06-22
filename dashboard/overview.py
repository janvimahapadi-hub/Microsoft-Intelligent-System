import streamlit as st
import pandas as pd

from utils.data_loader import get_project_overview


def show_overview():
    overview = get_project_overview()

    st.title("Company Overview")
    st.caption(
        "High-level system and company intelligence summary."
    )

    st.subheader("Company Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Company", overview["company_name"])

    with col2:
        st.metric("Industry", overview["industry"])

    st.subheader("Knowledge Repository Status")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Raw Documents", overview["raw_documents"])
    col2.metric("Cleaned Documents", overview["cleaned_documents"])
    col3.metric("Chunks", overview["chunks"])
    col4.metric("Indexed Vectors", overview["indexed_vectors"])

    st.subheader("Source Coverage")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Unique Sources", overview["unique_sources"])

    with col2:
        st.metric("Last Data Update", overview["last_update"])

    st.caption(
        f"Dashboard refresh time: {overview['dashboard_refresh']}"
    )

    st.divider()

    st.subheader("Documents by Source")

    source_stats = overview["source_stats"]

    if source_stats:
        source_df = pd.DataFrame(
            source_stats.items(),
            columns=["Source", "Document Count"]
        ).sort_values(
            by="Document Count",
            ascending=False
        )

        st.dataframe(
            source_df,
            use_container_width=True
        )

        st.bar_chart(
            source_df.set_index("Source")
        )
    else:
        st.warning("No source statistics available.")

    st.divider()

    st.subheader("Documents by Source Type")

    source_type_stats = overview["source_type_stats"]

    if source_type_stats:
        source_type_df = pd.DataFrame(
            source_type_stats.items(),
            columns=["Source Type", "Document Count"]
        ).sort_values(
            by="Document Count",
            ascending=False
        )

        st.dataframe(
            source_type_df,
            use_container_width=True
        )

        st.bar_chart(
            source_type_df.set_index("Source Type")
        )
    else:
        st.warning("No source type statistics available.")

    st.divider()

    st.subheader("Reliability Notes")

    st.info(
        "The system uses cached collected documents and a FAISS vector index for reliable demo performance. "
        "Live collectors can be rerun to refresh the repository, while the dashboard uses the latest indexed data."
    )