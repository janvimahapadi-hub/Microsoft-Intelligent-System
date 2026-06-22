import pandas as pd
import streamlit as st

from utils.data_loader import get_project_overview
from utils.pipeline_runner import (
    get_pipeline_script_status,
    get_manual_refresh_commands,
    run_audit,
    run_refresh_pipeline
)


def show_command_block(commands):
    command_text = "\n".join(commands)
    st.code(command_text, language="powershell")


def show_pipeline_result(result):
    step_name = result.get("step_name", result.get("step", "Unknown step"))
    success = result.get("success", False)

    if success:
        st.success(f"{step_name} completed successfully.")
    else:
        st.error(f"{step_name} failed.")

    with st.expander(f"Output: {step_name}"):
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")

        if stdout:
            st.write("**STDOUT:**")
            st.code(stdout)

        if stderr:
            st.write("**STDERR:**")
            st.code(stderr)

        st.write("**Return Code:**", result.get("return_code"))


def show_pipeline_status():
    st.title("Data Pipeline & Refresh")
    st.caption(
        "Manage collection, preprocessing, indexing, and audit status for the strategic intelligence repository."
    )

    overview = get_project_overview()

    st.subheader("Current Repository Health")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Raw Documents", overview["raw_documents"])
    col2.metric("Cleaned Documents", overview["cleaned_documents"])
    col3.metric("Chunks", overview["chunks"])
    col4.metric("Indexed Vectors", overview["indexed_vectors"])

    col5, col6 = st.columns(2)

    col5.metric("Unique Sources", overview["unique_sources"])
    col6.metric("Last Data Update", overview["last_update"])

    st.info(
        "For demo reliability, the dashboard uses cached indexed data. "
        "The refresh pipeline can be run to collect new data, rebuild chunks, regenerate embeddings, rebuild FAISS, and audit integrity."
    )

    st.divider()

    st.subheader("Pipeline Script Status")

    script_status = get_pipeline_script_status()

    status_df = pd.DataFrame(script_status)

    st.dataframe(
        status_df,
        use_container_width=True
    )

    missing_scripts = [
        item for item in script_status
        if not item["Exists"]
    ]

    if missing_scripts:
        st.warning(
            "Some pipeline scripts were not found. Check file names before running the full refresh pipeline."
        )
    else:
        st.success(
            "All expected pipeline scripts are available."
        )

    st.divider()

    st.subheader("Manual Refresh Commands")

    st.caption(
        "Use these commands from the project root if you want a controlled manual refresh."
    )

    show_command_block(
        get_manual_refresh_commands()
    )

    st.divider()

    st.subheader("Run Audit")

    st.caption(
        "Audit is safe to run during the demo because it only checks repository consistency."
    )

    if st.button("Run Repository Audit"):
        with st.spinner("Running audit..."):
            result = run_audit()

        result["step_name"] = "Repository Audit"
        show_pipeline_result(result)

    st.divider()

    st.subheader("Optional Refresh Pipeline")

    st.warning(
        "Only run the full refresh if you have enough time. Collection may require internet, and embedding/index rebuild may take longer."
    )

    run_collection = st.checkbox(
        "Run live collection",
        value=False,
        help="Runs collectors/manager.py. This may require internet and can be unstable during live demos."
    )

    run_cleaning = st.checkbox(
        "Run cleaning and deduplication",
        value=True
    )

    run_chunking = st.checkbox(
        "Run chunking",
        value=True
    )

    rebuild_embeddings = st.checkbox(
        "Rebuild embeddings",
        value=False,
        help="Can take time. Enable only when chunks changed."
    )

    rebuild_faiss = st.checkbox(
        "Rebuild FAISS index",
        value=False,
        help="Enable only if embeddings were rebuilt."
    )

    run_audit_after = st.checkbox(
        "Run audit after refresh",
        value=True
    )

    if rebuild_faiss and not rebuild_embeddings:
        st.warning(
            "FAISS rebuild usually requires fresh embeddings. Consider enabling 'Rebuild embeddings'."
        )

    if st.button("Run Selected Pipeline Steps"):
        with st.spinner("Running selected pipeline steps..."):
            results = run_refresh_pipeline(
                run_collection=run_collection,
                run_cleaning=run_cleaning,
                run_chunking=run_chunking,
                rebuild_embeddings=rebuild_embeddings,
                rebuild_faiss=rebuild_faiss,
                run_audit_after=run_audit_after
            )

        for result in results:
            show_pipeline_result(result)

    st.divider()

    st.subheader("Professional Deployment Note")

    st.info(
        "In a production system, the refresh pipeline would normally run as a scheduled background job. "
        "The Streamlit dashboard would read from the latest validated FAISS index rather than scraping live data during executive use."
    )