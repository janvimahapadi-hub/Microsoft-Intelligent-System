import streamlit as st

from intelligence.ceo_briefing import CEOBriefing


@st.cache_resource
def get_briefing_engine():
    return CEOBriefing(company_name="Microsoft")


def get_company(item):
    company = item.get("company", "")
    competitor = item.get("competitor", "")
    source = item.get("source", "")

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


def clean_preview_text(text, preview_length=700):
    if not text:
        return "No preview available."

    text = " ".join(text.split())

    if len(text) <= preview_length:
        return text

    trimmed = text[:preview_length]

    if " " in trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0]

    return trimmed + "..."


def show_evidence_diversity(evidence_items):
    companies = [get_company(item) for item in evidence_items]
    unique_companies = sorted(set(companies))

    microsoft_count = companies.count("Microsoft")
    competitor_count = len(companies) - microsoft_count

    col1, col2, col3 = st.columns(3)

    col1.metric("Evidence Items", len(evidence_items))
    col2.metric("Companies Used", len(unique_companies))
    col3.metric("Competitor Evidence", competitor_count)

    if unique_companies:
        st.write("**Companies in Evidence:**", ", ".join(unique_companies))
    else:
        st.write("**Companies in Evidence:** No evidence found")


def show_evidence_items(evidence_items, preview_length=700):
    for item in evidence_items:
        company = get_company(item)

        with st.expander(item.get("title", "Untitled evidence")):
            st.write("**Company:**", company)
            st.write("**Source:**", item.get("source", "Unknown source"))
            st.write("**Source Type:**", item.get("source_type", "unknown"))
            st.write("**Published:**", item.get("published", "unknown"))

            url = item.get("url", "")
            if url:
                st.markdown(f"**URL:** [{url}]({url})")

            st.write("**Evidence Preview:**")
            preview = clean_preview_text(
                item.get("evidence", ""),
                preview_length=preview_length
            )
            st.write(preview)


def clear_previous_briefing():
    keys_to_clear = [
        "latest_report",
        "latest_briefing",
        "latest_evidence",
        "latest_confidence",
        "latest_llm_status",
        "latest_markdown_report",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


def show_ceo_briefing():
    st.title("CEO Briefing")
    st.caption(
        "Generate evidence-based strategic briefings using RAG, hybrid retrieval, competitor sources, and a local open-source LLM."
    )

    default_question = "What cloud opportunities should Microsoft prioritize?"

    question = st.text_area(
        "Strategic Question",
        value=default_question,
        height=120,
        help="Ask a CEO-level strategic question."
    )

    st.markdown("##### Example Strategic Questions")

    example_questions = [
        "What AI strategy should Microsoft prioritize over the next 3 years?",
        "What are Microsoft's biggest cybersecurity risks?",
        "How should Microsoft compete against OpenAI, Google, and AWS?",
        "How should Microsoft compete with AWS and Google Cloud in AI infrastructure?",
        "What cloud opportunities should Microsoft prioritize?",
        "Which AI investments will generate the highest enterprise value?"
    ]

    selected_example = st.radio(
        "Choose an example question",
        ["Custom Question"] + example_questions,
        horizontal=False,
        index=0
    )

    if selected_example != "Custom Question":
        question = selected_example

    with st.expander("Retrieval Settings", expanded=False):
        top_k = st.slider(
            "Number of Evidence Chunks",
            min_value=3,
            max_value=6,
            value=4,
            help="Use 3-4 chunks for faster generation. Use more only if Ollama is running smoothly."
        )

    generation_mode = "fast"

    if st.button("Generate CEO Briefing"):
        if not question.strip():
            st.warning("Please enter a strategic question.")
            return

        st.session_state["followup_history"] = []
        clear_previous_briefing()

        with st.spinner("Retrieving evidence and generating strategic briefing..."):
            try:
                briefing_engine = get_briefing_engine()

                report = briefing_engine.generate(
                    strategic_question=question,
                    top_k=top_k,
                    mode=generation_mode
                )

                markdown_report = briefing_engine.generate_markdown_report(report)

                st.session_state["latest_report"] = report
                st.session_state["latest_briefing"] = report["briefing"]
                st.session_state["latest_evidence"] = report["evidence"]
                st.session_state["latest_confidence"] = report["retrieval_confidence"]
                st.session_state["latest_llm_status"] = report.get("llm_status", "")
                st.session_state["latest_markdown_report"] = markdown_report

            except Exception as error:
                st.error(f"Could not generate briefing: {error}")
                return

    if "latest_briefing" in st.session_state:
        st.divider()

        st.subheader("Executive Strategic Briefing")
        st.markdown(st.session_state["latest_briefing"])

        if "latest_markdown_report" in st.session_state:
            st.download_button(
                label="Download CEO Briefing",
                data=st.session_state["latest_markdown_report"],
                file_name="ceo_strategic_briefing.md",
                mime="text/markdown"
            )

        status = st.session_state.get("latest_llm_status", "")

        if "Fallback used" in status:
            st.warning(status)
        elif status:
            st.success(status)

        confidence = st.session_state.get("latest_confidence", 0.0)

        st.metric("Retrieval Confidence", f"{confidence:.2f}")
        st.progress(min(confidence, 1.0))

        if confidence < 0.7:
            st.info(
                "Confidence is moderate because evidence may be concentrated in limited sources. "
                "More competitor, market, or community evidence would improve confidence."
            )
        else:
            st.success(
                "Confidence is high because the recommendation is supported by diverse evidence items."
            )

        st.subheader("Evidence Diversity")
        show_evidence_diversity(
            st.session_state.get("latest_evidence", [])
        )

        st.subheader("Evidence Used")
        show_evidence_items(
            st.session_state.get("latest_evidence", []),
            preview_length=300
        )

    st.divider()

    st.subheader("Strategic Follow-up Q&A")
    st.caption(
        "Ask follow-up questions about recommendations, execution plans, risks, KPIs, evidence, or competitors."
    )

    followup_question = st.text_input(
        "Ask a strategic follow-up question",
        placeholder="Example: How should Microsoft execute this strategy in the next 90 days?"
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
                briefing_engine = get_briefing_engine()

                chat_result = briefing_engine.analyzer.answer_followup(
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

            st.markdown("#### Evidence Used for Follow-up")
            show_evidence_items(
                chat_item.get("evidence", []),
                preview_length=600
            )

            st.divider()