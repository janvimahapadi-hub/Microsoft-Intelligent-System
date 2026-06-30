import json
import html

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
    if "anthropic" in source_lower:
        return "Anthropic"

    return "Microsoft"


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def clean_preview_text(text, preview_length=700):
    if not text:
        return "No preview available."

    text = " ".join(str(text).split())

    if len(text) <= preview_length:
        return text

    trimmed = text[:preview_length]

    if " " in trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0]

    return trimmed + "..."


def show_readable_json(data, height=260):
    try:
        readable_text = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str
        )
    except Exception:
        readable_text = str(data)

    escaped_text = html.escape(readable_text)

    st.markdown(
        f"""
        <div style="
            background-color: #f8fafc;
            color: #111827;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 16px;
            max-height: {height}px;
            overflow-y: auto;
            font-family: Consolas, Monaco, 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
        ">{escaped_text}</div>
        """,
        unsafe_allow_html=True
    )


def show_signal_items(title, items):
    st.markdown(f"#### {title}")

    if not items:
        st.info("No evidence items found for this signal.")
        return

    for index, item in enumerate(items, start=1):
        item_title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        company = item.get("company", "Unknown company")
        topic = item.get("topic", "Unknown topic")
        sentiment = item.get("sentiment", "Unknown sentiment")
        url = item.get("url", "")
        preview = item.get("evidence_preview", "")

        with st.expander(f"{index}. {item_title}"):
            st.write("**Company:**", company)
            st.write("**Source:**", source)
            st.write("**Topic:**", topic)
            st.write("**Sentiment:**", sentiment)

            if url:
                st.markdown(f"**URL:** [{url}]({url})")

            if preview:
                st.write("**Evidence Preview:**")
                st.write(clean_preview_text(preview, preview_length=300))


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
    if not evidence_items:
        st.info("No evidence items available.")
        return

    for item in evidence_items:
        company = get_company(item)
        title = item.get("title", "Untitled evidence")

        with st.expander(title):
            st.write("**Company:**", company)
            st.write("**Source:**", item.get("source", "Unknown source"))
            st.write("**Source Type:**", item.get("source_type", "unknown"))
            st.write("**Published:**", item.get("published", "unknown"))

            url = item.get("url", "")

            if url:
                st.markdown(f"**URL:** [{url}]({url})")

            st.write("**Evidence Preview:**")

            evidence_text = (
                item.get("evidence")
                or item.get("chunk_text")
                or item.get("text")
                or ""
            )

            preview = clean_preview_text(
                evidence_text,
                preview_length=preview_length
            )

            st.write(preview)


def show_validation_gate(agent_result):
    validation = agent_result.get("validation", {})
    decision = agent_result.get("decision", {})

    if not validation:
        st.warning("No validation result available.")
        return

    st.subheader("Validation Before Recommendation")

    confidence = safe_float(validation.get("confidence", 0.0))
    status = validation.get("validation_status", "Unknown")
    ready = validation.get("is_ready_for_recommendation", False)
    warnings = validation.get("warnings", [])

    col1, col2, col3 = st.columns(3)

    col1.metric("Validation Status", status)
    col2.metric("Validation Confidence", round(confidence, 2))
    col3.metric("Ready for Recommendation", "Yes" if ready else "No")

    st.progress(min(confidence, 1.0))

    if ready:
        st.success(
            decision.get(
                "decision_status",
                "Recommendation passed validation and can be presented."
            )
        )
    else:
        st.warning(
            decision.get(
                "decision_status",
                "Recommendation requires caution because validation confidence is weak."
            )
        )

    if warnings:
        st.write("**Validation Warnings:**")
        for warning in warnings:
            st.markdown(f"- {warning}")
    else:
        st.write("**Validation Warnings:** None")


def show_agent_workflow_trace(agent_result):
    if not agent_result:
        st.warning("No agent workflow trace available.")
        return

    st.subheader("Agent Workflow Trace")

    st.caption(
        "This section shows explicit agent behaviour: planning, autonomous tool selection, retrieval, analysis, decision-making, validation, and memory."
    )

    workflow = agent_result.get("workflow", [])

    if workflow:
        st.write("**Workflow executed:**")
        for step in workflow:
            st.markdown(f"- {step}")

    with st.expander("1. Goal", expanded=True):
        st.write(agent_result.get("goal", "No goal available."))

    with st.expander("2. Plan created by PlannerAgent", expanded=True):
        plan = agent_result.get("plan", {})

        st.write("**Detected question type:**")
        st.success(plan.get("question_type", "unknown"))

        st.write("**Planned steps:**")

        steps = plan.get("steps", [])

        if steps:
            for step in steps:
                st.markdown(f"- {step}")
        else:
            st.write("No planned steps available.")

        st.write("**Raw plan object:**")
        show_readable_json(plan, height=240)

    with st.expander("3. Autonomous Tool Decision by ToolAgent", expanded=False):
        tool_decision = agent_result.get("tool_decision", {})
        selected_tools = tool_decision.get("selected_tools", [])
        decision_reasoning = tool_decision.get("decision_reasoning", [])

        st.write("**Selected tools:**")

        if selected_tools:
            for tool in selected_tools:
                st.markdown(f"- `{tool}`")
        else:
            st.write("No tools selected.")

        st.write("**Tool selection reasoning:**")

        if decision_reasoning:
            for reason in decision_reasoning:
                st.markdown(f"- {reason}")
        else:
            st.info(tool_decision.get("reason", "No reason available."))

        st.write("**Raw tool decision object:**")
        show_readable_json(tool_decision, height=220)

    with st.expander("4. Evidence Retrieval", expanded=False):
        retrieval = agent_result.get("retrieval", {})
        queries_used = retrieval.get("queries_used", [])

        retrieval_count = retrieval.get(
            "retrieval_count",
            len(retrieval.get("evidence", []))
        )

        st.write("**Evidence retrieved:**")
        st.metric("Retrieved Evidence Items", retrieval_count)

        st.write("**Queries used by the agent:**")

        if queries_used:
            for query in queries_used:
                st.markdown(f"- {query}")
        else:
            st.write("No retrieval queries available.")

    with st.expander("5. Strategic Analysis", expanded=True):
        analysis = agent_result.get("analysis", {})

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Risk Signals", analysis.get("risk_count", 0))
        col2.metric("Opportunity Signals", analysis.get("opportunity_count", 0))
        col3.metric("Competitor Signals", analysis.get("competitor_count", 0))
        col4.metric("Market Signals", analysis.get("market_count", 0))

        analysis_summary = analysis.get("analysis_summary", {})

        st.write("**Analysis summary:**")

        if analysis_summary:
            dominant_signal = analysis_summary.get("dominant_signal", "Unknown")
            competitor_context = analysis_summary.get("has_competitor_context", False)
            market_context = analysis_summary.get("has_market_context", False)

            st.markdown(f"- **Dominant signal:** {dominant_signal}")
            st.markdown(f"- **Has competitor context:** {'Yes' if competitor_context else 'No'}")
            st.markdown(f"- **Has market context:** {'Yes' if market_context else 'No'}")
        else:
            st.write("No analysis summary available.")

        st.divider()

        show_signal_items(
            "Risk Evidence Items",
            analysis.get("risk_items", [])
        )

        show_signal_items(
            "Opportunity Evidence Items",
            analysis.get("opportunity_items", [])
        )

        show_signal_items(
            "Competitor Evidence Items",
            analysis.get("competitor_items", [])
        )

        show_signal_items(
            "Market Evidence Items",
            analysis.get("market_items", [])
        )

        st.write("**Raw analysis object:**")
        show_readable_json(analysis, height=300)

    with st.expander("6. Validation by ValidationAgent", expanded=False):
        validation = agent_result.get("validation", {})

        if validation:
            confidence = safe_float(validation.get("confidence", 0.0))
            status = validation.get("validation_status", "Unknown")
            ready = validation.get("is_ready_for_recommendation", False)

            col1, col2, col3 = st.columns(3)

            col1.metric("Status", status)
            col2.metric("Confidence", round(confidence, 2))
            col3.metric("Ready", "Yes" if ready else "No")

        st.write("**Raw validation object:**")
        show_readable_json(validation, height=260)

    with st.expander("7. Agent Decision", expanded=False):
        decision = agent_result.get("decision", {})

        if decision:
            st.write("**Decision status:**")
            st.info(decision.get("decision_status", "No decision status available."))

            st.write("**Selected tools used for decision:**")
            for tool in decision.get("selected_tools", []):
                st.markdown(f"- `{tool}`")

            tool_reason = decision.get("tool_selection_reason", [])

            st.write("**Tool selection reasons:**")
            if isinstance(tool_reason, list):
                for reason in tool_reason:
                    st.markdown(f"- {reason}")
            else:
                st.write(tool_reason)

            warnings = decision.get("warnings", [])

            if warnings:
                st.write("**Warnings:**")
                for warning in warnings:
                    st.markdown(f"- {warning}")
            else:
                st.write("**Warnings:** None")

        st.write("**Raw decision object:**")
        show_readable_json(decision, height=260)

    with st.expander("8. Memory Context", expanded=False):
        memory_context = agent_result.get("memory_context", "")

        if memory_context:
            st.write(memory_context)
        else:
            st.write("No memory context available yet.")


def normalize_agent_result(report):
    agent_result = report.get("agent_result", {}) or {}

    validation = report.get("validation", {}) or {}
    agent_decision = report.get("agent_decision", {}) or {}

    if validation and "validation" not in agent_result:
        agent_result["validation"] = validation

    if agent_decision and "decision" not in agent_result:
        agent_result["decision"] = agent_decision

    if "goal" not in agent_result:
        agent_result["goal"] = report.get("question", "")

    return agent_result


def clear_previous_briefing():
    keys_to_clear = [
        "latest_report",
        "latest_briefing",
        "latest_evidence",
        "latest_confidence",
        "latest_llm_status",
        "latest_markdown_report",
        "latest_agent_result",
        "latest_validation",
        "latest_agent_decision",
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

        with st.spinner("Retrieving evidence, executing agent workflow, validating recommendation, and generating strategic briefing..."):
            try:
                briefing_engine = get_briefing_engine()

                report = briefing_engine.generate(
                    strategic_question=question,
                    top_k=top_k,
                    mode=generation_mode
                )

                markdown_report = briefing_engine.generate_markdown_report(report)
                agent_result = normalize_agent_result(report)

                st.session_state["latest_report"] = report
                st.session_state["latest_briefing"] = report["briefing"]
                st.session_state["latest_evidence"] = report["evidence"]
                st.session_state["latest_confidence"] = report["retrieval_confidence"]
                st.session_state["latest_llm_status"] = report.get("llm_status", "")
                st.session_state["latest_markdown_report"] = markdown_report

                st.session_state["latest_agent_result"] = agent_result
                st.session_state["latest_validation"] = agent_result.get("validation", {})
                st.session_state["latest_agent_decision"] = agent_result.get("decision", {})

            except Exception as error:
                st.error(f"Could not generate briefing: {error}")
                return

    if "latest_briefing" in st.session_state:
        st.divider()

        agent_result = st.session_state.get("latest_agent_result", {})

        show_validation_gate(agent_result)

        st.divider()

        show_agent_workflow_trace(agent_result)

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

        confidence = safe_float(st.session_state.get("latest_confidence", 0.0))

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

            with st.spinner("Thinking through the follow-up question using briefing memory and retrieved evidence..."):
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