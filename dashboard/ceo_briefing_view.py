import streamlit as st

from intelligence.strategic_analyzer import StrategicAnalyzer


@st.cache_resource
def get_analyzer():
    """
    Cache the retriever, embedding model, FAISS index, and metadata.
    This prevents Streamlit from reloading everything on every interaction.
    """
    return StrategicAnalyzer(company_name="Microsoft")


def show_evidence_items(evidence_items, preview_length=700):
    for item in evidence_items:
        with st.expander(item.get("title", "Untitled evidence")):
            st.write("**Source:**", item.get("source", "Unknown source"))
            st.write("**Source Type:**", item.get("source_type", "unknown"))
            st.write("**Published:**", item.get("published", "unknown"))

            url = item.get("url", "")
            if url:
                st.markdown(f"**URL:** [{url}]({url})")

            st.write("**Evidence Preview:**")
            st.write(item.get("evidence", "")[:preview_length])


def show_ceo_briefing():
    st.title("CEO Briefing")
    st.caption(
        "Evidence-based strategic briefing generated using RAG and a local open-source LLM."
    )

    default_question = (
        "Based on the retrieved evidence, what AI strategy should Microsoft prioritize next?"
    )

    question = st.text_area(
        "Strategic question",
        value=default_question,
        height=100
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        generation_mode_label = st.radio(
            "Generation mode",
            ["Fast Briefing", "Deep Strategic Playbook"],
            index=0
        )

    with col2:
        top_k = st.slider(
            "Number of evidence chunks to retrieve",
            min_value=2,
            max_value=5,
            value=3
        )

    if generation_mode_label == "Fast Briefing":
        generation_mode = "fast"
    else:
        generation_mode = "playbook"

    if st.button("Generate CEO Briefing"):
        if not question.strip():
            st.warning("Please enter a strategic question.")
            return

        with st.spinner("Retrieving evidence and generating strategic briefing..."):
            try:
                analyzer = get_analyzer()

                result = analyzer.analyze(
                    strategic_question=question,
                    top_k=top_k,
                    mode=generation_mode
                )

                st.session_state["latest_briefing"] = result["answer"]
                st.session_state["latest_evidence"] = result["evidence"]
                st.session_state["latest_confidence"] = result["retrieval_confidence"]
                st.session_state["latest_llm_status"] = result.get("llm_status", "")

            except Exception as error:
                st.error(f"Could not generate briefing: {error}")
                return

    if "latest_briefing" in st.session_state:
        st.subheader("Executive Strategic Briefing")
        st.markdown(st.session_state["latest_briefing"])

        status = st.session_state.get("latest_llm_status", "")

        if "Fallback used" in status:
            st.warning(status)
        elif status:
            st.success(status)

        confidence = st.session_state.get("latest_confidence", 0.0)

        st.metric(
            "Retrieval Confidence",
            confidence
        )

        if confidence < 0.7:
            st.info(
                "Confidence is moderate because the retrieved evidence may be concentrated in a limited number of sources. "
                "More competitor, market, or community evidence would improve confidence."
            )
        else:
            st.success(
                "Confidence is high because the recommendation is supported by multiple evidence items."
            )

        st.subheader("Evidence Used")
        show_evidence_items(
            st.session_state.get("latest_evidence", []),
            preview_length=700
        )

    st.divider()

    st.subheader("Strategic Follow-up Q&A")
    st.caption(
        "Ask follow-up questions about the recommendation, execution plan, risks, KPIs, or evidence."
    )

    followup_question = st.text_input(
        "Ask a strategic follow-up question",
        placeholder="Example: How should Microsoft execute Action 1 in the next 90 days?"
    )

    if "followup_history" not in st.session_state:
        st.session_state["followup_history"] = []

    if st.button("Ask Follow-up"):
        if "latest_briefing" not in st.session_state:
            st.warning("Generate a CEO briefing first before asking follow-up questions.")
            return

        if not followup_question.strip():
            st.warning("Please enter a follow-up question.")
            return

        with st.spinner("Thinking through the follow-up question..."):
            try:
                analyzer = get_analyzer()

                chat_result = analyzer.answer_followup(
                    user_question=followup_question,
                    previous_briefing=st.session_state["latest_briefing"],
                    top_k=3,
                    mode="chat"
                )

                st.session_state["followup_history"].append(chat_result)

            except Exception as error:
                st.error(f"Could not answer follow-up question: {error}")
                return

    if st.session_state["followup_history"]:
        st.markdown("### Follow-up Conversation")

        for chat_item in reversed(st.session_state["followup_history"]):
            st.markdown("#### Question")
            st.write(chat_item["question"])

            status = chat_item.get("llm_status", "")
            if "Fallback used" in status:
                st.warning(status)
            elif status:
                st.success(status)

            st.markdown("#### Answer")
            st.markdown(chat_item["answer"])

            st.markdown("#### Evidence used for follow-up")
            show_evidence_items(
                chat_item.get("evidence", []),
                preview_length=600
            )

            st.divider()