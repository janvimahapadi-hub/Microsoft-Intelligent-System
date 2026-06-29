from agents.strategic_agent import StrategicAgent
from retrieval.hybrid_retriever import HybridRetriever

from llm.ollama_client import generate_response
from llm.prompts import (
    FAST_CEO_SYSTEM_PROMPT,
    CEO_SYSTEM_PROMPT,
    build_ceo_prompt,
    CHATBOT_SYSTEM_PROMPT,
    build_chat_prompt
)


def get_company_name(item):
    company = (
        item.get("company")
        or item.get("competitor")
        or item.get("source")
        or "Unknown"
    )

    source = item.get("source", "").lower()

    if company and company != "Unknown":
        return company

    if "aws" in source:
        return "AWS"
    if "google" in source:
        return "Google Cloud"
    if "openai" in source:
        return "OpenAI"
    if "nvidia" in source:
        return "NVIDIA"
    if "anthropic" in source:
        return "Anthropic"

    return "Microsoft"


def deduplicate_evidence(evidence_items, max_items=5):
    seen = set()
    unique_items = []

    for item in evidence_items:
        key = item.get("url") or item.get("title") or str(item.get("chunk_id"))

        if key in seen:
            continue

        seen.add(key)
        unique_items.append(item)

    unique_items = sorted(
        unique_items,
        key=lambda x: x.get("score", 999999)
    )

    return unique_items[:max_items]


def is_bad_evidence(item):
    title = item.get("title", "").lower()
    source = item.get("source", "").lower()
    evidence = item.get("evidence", "").lower()

    bad_terms = [
        "weekly employment",
        "employment q&a",
        "job search",
        "resume",
        "interview",
        "hiring",
        "study buddy",
        "open to work"
    ]

    if any(term in title or term in evidence for term in bad_terms):
        return True

    if "reddit" in source and any(term in title for term in bad_terms):
        return True

    return False

def is_incomplete_answer(answer):
    """
    Practical completeness check for local Ollama models.

    We do not require an exact END marker because small local models may skip it.
    Instead, we check whether the answer contains enough CEO briefing structure.
    """

    if not answer or len(answer.strip()) < 350:
        return True

    answer_lower = answer.lower()

    important_sections = [
        "executive diagnosis",
        "recommended ceo decision",
        "90-day",
        "owners",
        "kpi",
        "risk",
        "evidence used"
    ]

    found_sections = 0

    for section in important_sections:
        if section in answer_lower:
            found_sections += 1

    # Evidence section is important because it usually appears near the end.
    has_evidence_section = "evidence used" in answer_lower

    # Accept if it has evidence and most required sections.
    if has_evidence_section and found_sections >= 5:
        return False

    return True

def build_fallback_playbook(company_name, strategic_question, evidence_items, error_message):
    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        company = get_company_name(item)
        evidence_titles.append(f"- {title} ({source}, {company})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## 1. Executive diagnosis

The system retrieved evidence for the question: **{strategic_question}**.

The local LLM was too slow, unavailable, or returned an incomplete response, so this fallback playbook was created using retrieved evidence metadata.

## 2. Strategic meaning

The evidence indicates that {company_name} should evaluate this topic through business impact, execution feasibility, competitive positioning, and strategic risk.

## 3. Priority opportunities

1. **Scale enterprise AI infrastructure**
   - Focus on Azure AI, Microsoft Foundry, enterprise agents, and secure AI deployment.

2. **Strengthen ecosystem and partner-led adoption**
   - Use partners, developers, and enterprise channels to accelerate adoption.

3. **Improve governance and security differentiation**
   - Make trust, security, compliance, and governance core differentiators.

## 4. 90-day execution plan

### First 30 days
- Identify top evidence-backed opportunity themes.
- Assign owners.
- Define KPIs.

### Days 31-60
- Launch focused pilots.
- Validate feasibility and customer value.
- Compare Microsoft positioning against competitor evidence.

### Days 61-90
- Scale the strongest pilot.
- Publish KPI results.
- Decide whether to expand, refine, or stop the initiative.

## 5. Owners and KPIs

- **Owners:** Azure, AI Platform, Security, Product Strategy, Sales, Partner Ecosystem.
- **KPIs:** adoption, deployment speed, governance coverage, customer pipeline impact.

## 6. Main risks and mitigations

- **Risk:** Limited evidence diversity.  
  **Mitigation:** Add competitor, market, and customer evidence.

- **Risk:** Recommendations may be broad.  
  **Mitigation:** Require owner, KPI, timeline, and evidence.

- **Risk:** Local LLM may be slow.  
  **Mitigation:** Use fast mode and fallback output.

## 7. Evidence used

{evidence_text}

---

Fallback reason: {error_message}
"""


def build_fallback_chat_answer(company_name, user_question, evidence_items, error_message):
    evidence_titles = []

    for item in evidence_items:
        title = item.get("title", "Unknown title")
        source = item.get("source", "Unknown source")
        company = get_company_name(item)
        evidence_titles.append(f"- {title} ({source}, {company})")

    evidence_text = "\n".join(evidence_titles)

    return f"""
## Follow-up answer

The system retrieved evidence for the follow-up question: **{user_question}**.

The local LLM was too slow, unavailable, or returned an incomplete response. This fallback answer is based on retrieved evidence metadata.

### Practical next step

Use the retrieved evidence to create a focused execution plan with:

1. A clear business owner
2. A 30-60-90 day timeline
3. 2-3 measurable KPIs
4. Main risks and mitigations
5. Additional evidence needed before final decision

### Evidence retrieved

{evidence_text}

Fallback reason: {error_message}
"""


class StrategicAnalyzer:
    def __init__(self, company_name="Microsoft"):
        self.company_name = company_name

        # Backup/simple retrieval
        self.retriever = HybridRetriever()

        # Agentic workflow layer
        self.agent = StrategicAgent()

    def retrieve_strategic_evidence(self, strategic_question, top_k=5):
        """
        Backup retrieval if the agent workflow fails.
        """

        raw_results = self.retriever.search(
            strategic_question,
            top_k=top_k * 3
        )

        clean_evidence = [
            item for item in raw_results
            if not is_bad_evidence(item)
        ]

        return deduplicate_evidence(
            clean_evidence,
            max_items=top_k
        )

    def build_agent_context_text(self, agent_result):
        plan = agent_result.get("plan", {})
        tool_decision = agent_result.get("tool_decision", {})
        analysis = agent_result.get("analysis", {})
        validation = agent_result.get("validation", {})
        memory_context = agent_result.get("memory_context", "")

        plan_steps = plan.get("steps", [])
        selected_tools = tool_decision.get("selected_tools", [])
        warnings = validation.get("warnings", [])

        return f"""
Agent Workflow Summary:

Goal:
{agent_result.get("goal", "")}

Plan:
{chr(10).join("- " + step for step in plan_steps)}

Selected Tools:
{", ".join(selected_tools)}

Analysis:
- Dominant signal: {analysis.get("analysis_summary", {}).get("dominant_signal", "Unknown")}
- Risk evidence count: {analysis.get("risk_count", 0)}
- Opportunity evidence count: {analysis.get("opportunity_count", 0)}
- Competitor evidence count: {analysis.get("competitor_count", 0)}
- Market evidence count: {analysis.get("market_count", 0)}
- Dashboard risk signals: {analysis.get("dashboard_risk_signals", 0)}
- Dashboard opportunity signals: {analysis.get("dashboard_opportunity_signals", 0)}

Validation:
- Status: {validation.get("validation_status", "Unknown")}
- Confidence: {validation.get("confidence", 0.0)}
- Evidence count: {validation.get("evidence_count", 0)}
- Source count: {validation.get("source_count", 0)}
- Company count: {validation.get("company_count", 0)}
- Warnings: {", ".join(warnings) if warnings else "No major validation warnings"}

Memory:
{memory_context}
"""

    def build_agent_decision(self, agent_result):
        """
        Converts validation + tool decision into a clear decision object
        for dashboard display and examiner explanation.
        """

        validation = agent_result.get("validation", {})
        tool_decision = agent_result.get("tool_decision", {})

        confidence = validation.get("confidence", 0.0)
        ready = validation.get("is_ready_for_recommendation", False)
        validation_status = validation.get("validation_status", "Unknown")
        warnings = validation.get("warnings", [])
        selected_tools = tool_decision.get("selected_tools", [])

        if ready:
            decision_status = "Recommendation approved for presentation"
        else:
            decision_status = "Recommendation requires caution because validation confidence is weak"

        return {
            "selected_tools": selected_tools,
            "tool_selection_reason": tool_decision.get(
                "reason",
                "No tool selection reason available."
            ),
            "validation_status": validation_status,
            "confidence": confidence,
            "ready_for_recommendation": ready,
            "decision_status": decision_status,
            "warnings": warnings
        }

    def get_memory_safely(self):
        try:
            return self.agent.memory_agent.get_recent_memory()
        except Exception:
            return []

    def get_memory_context_safely(self):
        try:
            return self.agent.memory_agent.build_memory_context()
        except Exception:
            return "Memory context unavailable."

    def update_latest_answer_safely(self, answer):
        try:
            self.agent.memory_agent.update_latest_answer(answer)
        except Exception:
            pass

    def analyze(self, strategic_question, top_k=5, mode="fast"):
        """
        Main agentic workflow:

        Goal
          ↓
        Plan
          ↓
        Tool Selection
          ↓
        Retrieve
          ↓
        Analyze
          ↓
        Validate
          ↓
        Recommend
          ↓
        Store Memory
        """

        try:
            agent_result = self.agent.execute(
                user_goal=strategic_question,
                top_k=top_k
            )

            evidence_items = agent_result.get("evidence", [])

            evidence_items = [
                item for item in evidence_items
                if not is_bad_evidence(item)
            ]

            evidence_items = deduplicate_evidence(
                evidence_items,
                max_items=top_k
            )

            confidence = agent_result.get("confidence", 0.0)
            agent_context = self.build_agent_context_text(agent_result)

        except Exception as agent_error:
            evidence_items = self.retrieve_strategic_evidence(
                strategic_question,
                top_k=top_k
            )

            confidence = 0.50

            agent_result = {
                "error": str(agent_error),
                "goal": strategic_question,
                "workflow": [
                    "Goal received",
                    "Agent workflow failed",
                    "Backup retrieval used",
                    "Fallback validation created"
                ],
                "plan": {
                    "question_type": "fallback",
                    "steps": [
                        "Use backup retrieval",
                        "Filter bad evidence",
                        "Generate fallback briefing"
                    ]
                },
                "tool_decision": {
                    "selected_tools": ["backup_hybrid_retrieval"],
                    "reason": "Agent workflow failed, so backup retrieval was selected."
                },
                "retrieval": {
                    "queries_used": [strategic_question],
                    "retrieval_count": len(evidence_items),
                    "evidence": evidence_items
                },
                "analysis": {
                    "risk_count": 0,
                    "opportunity_count": 0,
                    "competitor_count": 0,
                    "market_count": 0,
                    "dashboard_risk_signals": 0,
                    "dashboard_opportunity_signals": 0,
                    "analysis_summary": {
                        "dominant_signal": "Fallback mode"
                    }
                },
                "validation": {
                    "validation_status": "Fallback",
                    "confidence": confidence,
                    "evidence_count": len(evidence_items),
                    "source_count": len(set(item.get("source", "") for item in evidence_items)),
                    "company_count": len(set(get_company_name(item) for item in evidence_items)),
                    "is_ready_for_recommendation": False,
                    "warnings": [str(agent_error)]
                },
                "memory_context": "Agent memory unavailable because agent workflow failed."
            }

            agent_context = f"""
Agent Workflow Summary:
The agent workflow failed, so backup retrieval was used.

Agent error:
{agent_error}
"""

        user_prompt = build_ceo_prompt(
            company_name=self.company_name,
            strategic_question=strategic_question,
            evidence_items=evidence_items
        )

        user_prompt = f"""
{agent_context}

{user_prompt}

Additional instruction:
Use the agent plan, selected tools, analysis, validation result, and memory context when forming the recommendation.
If validation status is weak or warnings exist, mention the limitation clearly.

Write the final CEO briefing in these sections:

## 1. Executive diagnosis
2-3 sentences only.

## 2. Recommended CEO decision
Give one clear decision.

## 3. 90-day execution plan
Use exactly three bullets:
- First 30 days:
- Days 31-60:
- Days 61-90:

## 4. Owners and KPIs
Mention owners and 3 measurable KPIs.

## 5. Main risks and mitigations
Mention 2-3 risks with mitigation.

## 6. Evidence used
Mention 3-5 evidence titles or source names.

Keep the answer concise and finish with the Evidence used section.
Do not add extra commentary after the evidence section.
"""

        try:
            selected_prompt = (
                FAST_CEO_SYSTEM_PROMPT
                if mode == "fast"
                else CEO_SYSTEM_PROMPT
            )

            answer = generate_response(
                system_prompt=selected_prompt,
                user_prompt=user_prompt,
                mode=mode
            )

            if is_incomplete_answer(answer):
                raise RuntimeError(
                    "LLM response was incomplete. Using fallback playbook."
                )

            llm_status = "LLM generation successful with agent workflow"

            # Store final generated answer in memory
            self.update_latest_answer_safely(answer)

        except Exception as error:
            answer = build_fallback_playbook(
                company_name=self.company_name,
                strategic_question=strategic_question,
                evidence_items=evidence_items,
                error_message=str(error)
            )

            llm_status = f"Fallback used because LLM failed: {error}"

            # Store fallback answer in memory too
            self.update_latest_answer_safely(answer)

        # Keep agent result synchronized with the cleaned evidence used in the final answer.
        agent_result["evidence"] = evidence_items
        agent_result["confidence"] = confidence

        if "workflow" not in agent_result:
            agent_result["workflow"] = [
                "Goal received",
                "Plan created",
                "Tools selected autonomously",
                "Evidence retrieved",
                "Analysis completed",
                "Validation completed",
                "Recommendation generated"
            ]

        if "retrieval" not in agent_result:
            agent_result["retrieval"] = {
                "queries_used": [strategic_question],
                "retrieval_count": len(evidence_items),
                "evidence": evidence_items
            }
        else:
            agent_result["retrieval"]["evidence"] = evidence_items
            agent_result["retrieval"]["retrieval_count"] = len(evidence_items)

            if "queries_used" not in agent_result["retrieval"]:
                agent_result["retrieval"]["queries_used"] = [strategic_question]

        agent_decision = agent_result.get("decision")

        if not agent_decision:
            agent_decision = self.build_agent_decision(agent_result)
            agent_result["decision"] = agent_decision

        validation = agent_result.get("validation", {})

        return {
            "company": self.company_name,
            "question": strategic_question,
            "retrieval_confidence": confidence,
            "answer": answer,
            "evidence": evidence_items,
            "llm_status": llm_status,

            # Full agent object for dashboard workflow trace
            "agent_result": agent_result,
            "validation": validation,
            "agent_decision": agent_decision,

            # Backward-compatible fields already used by your current code
            "agent_plan": agent_result.get("plan", {}),
            "agent_tools": agent_result.get("tool_decision", {}),
            "agent_analysis": agent_result.get("analysis", {}),
            "agent_validation": validation,
            "agent_memory": self.get_memory_safely(),
            "agent_memory_context": self.get_memory_context_safely(),
            "agent_workflow": agent_result.get("workflow", [])
        }

    def answer_followup(self, user_question, previous_briefing="", top_k=3, mode="chat"):
        followup_query = (
            user_question
            + " Microsoft AI strategy Azure Copilot Foundry partner ecosystem execution roadmap"
        )

        raw_evidence = self.retriever.search(
            followup_query,
            top_k=top_k * 4
        )

        evidence_items = [
            item for item in raw_evidence
            if not is_bad_evidence(item)
        ]

        evidence_items = deduplicate_evidence(
            evidence_items,
            max_items=top_k
        )

        memory_context = self.get_memory_context_safely()

        user_prompt = build_chat_prompt(
            company_name=self.company_name,
            user_question=user_question,
            previous_briefing=previous_briefing + "\n\nAgent Memory:\n" + memory_context,
            evidence_items=evidence_items
        )

        try:
            answer = generate_response(
                system_prompt=CHATBOT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                mode=mode
            )

            if not answer or len(answer.strip()) < 50:
                raise RuntimeError(
                    "LLM follow-up response was empty or incomplete."
                )

            llm_status = "LLM follow-up generation successful with memory"

        except Exception as error:
            answer = build_fallback_chat_answer(
                company_name=self.company_name,
                user_question=user_question,
                evidence_items=evidence_items,
                error_message=str(error)
            )

            llm_status = f"Fallback used because LLM failed: {error}"

        return {
            "question": user_question,
            "answer": answer,
            "evidence": evidence_items,
            "llm_status": llm_status,
            "agent_memory": self.get_memory_safely()
        }


if __name__ == "__main__":
    analyzer = StrategicAnalyzer(company_name="Microsoft")

    question = "What cloud opportunities should Microsoft prioritize?"

    result = analyzer.analyze(
        strategic_question=question,
        top_k=5,
        mode="fast"
    )

    print("\n" + "=" * 120)
    print("AI CEO STRATEGIC BRIEFING")
    print("=" * 120)
    print(result["answer"])

    print("\n" + "=" * 120)
    print("RETRIEVAL CONFIDENCE:", result["retrieval_confidence"])
    print("LLM STATUS:", result["llm_status"])
    print("=" * 120)

    print("\nAGENT PLAN")
    print("=" * 120)
    print(result["agent_plan"])

    print("\nAGENT TOOLS")
    print("=" * 120)
    print(result["agent_tools"])

    print("\nAGENT VALIDATION")
    print("=" * 120)
    print(result["agent_validation"])

    print("\nAGENT DECISION")
    print("=" * 120)
    print(result["agent_decision"])

    print("\nAGENT WORKFLOW")
    print("=" * 120)
    print(result["agent_workflow"])

    print("\nAGENT MEMORY")
    print("=" * 120)
    print(result["agent_memory"])

    print("\nEVIDENCE USED")
    print("=" * 120)

    for item in result["evidence"]:
        print("\n" + "-" * 100)
        print("Title:", item.get("title"))
        print("Source:", item.get("source"))
        print("Company:", get_company_name(item))
        print("Source Type:", item.get("source_type"))
        print("Published:", item.get("published"))
        print("URL:", item.get("url"))
        print("Evidence Preview:")
        print(item.get("evidence", "")[:400])