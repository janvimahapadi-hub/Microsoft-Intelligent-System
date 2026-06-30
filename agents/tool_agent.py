class ToolAgent:
    """
    Tool Agent:
    Decides which tools should be used for a given strategic plan.

    It does not execute tools directly.
    It selects tools and gives reasons so the StrategicAgent can execute them.
    """

    def select_tools(self, plan):
        goal = plan.get("goal", "").lower()
        question_type = plan.get("question_type", "general_strategy")

        selected_tools = []
        reasons = []

        # Hybrid retrieval is always needed for evidence-based RAG
        selected_tools.append("hybrid_retrieval")
        reasons.append("Hybrid retrieval is required to collect evidence before LLM generation.")

        if (
            question_type == "competitor_strategy"
            or any(word in goal for word in ["competitor", "compete", "aws", "google", "openai", "nvidia", "anthropic"])
        ):
            selected_tools.append("competitor_intelligence")
            reasons.append("Competitor intelligence selected because the question mentions competitors or competitive positioning.")

        if (
            question_type == "risk_strategy"
            or any(word in goal for word in ["risk", "security", "threat", "governance", "compliance", "regulation", "privacy"])
        ):
            selected_tools.append("risk_analysis")
            reasons.append("Risk analysis selected because the question contains risk, security, governance, or compliance intent.")

        if (
            question_type == "opportunity_strategy"
            or any(word in goal for word in ["opportunity", "growth", "investment", "prioritize", "scale", "adoption"])
        ):
            selected_tools.append("opportunity_analysis")
            reasons.append("Opportunity analysis selected because the question asks about growth, prioritization, investment, or adoption.")

        if (
            question_type == "market_strategy"
            or any(word in goal for word in ["market", "trend", "industry", "customer", "enterprise"])
        ):
            selected_tools.append("market_intelligence")
            reasons.append("Market intelligence selected because the question involves market, industry, customer, or enterprise trends.")

        # LLM generation is always needed at the final recommendation step
        selected_tools.append("llm_generation")
        reasons.append("LLM generation selected to convert evidence and analysis into a CEO briefing.")

        selected_tools = list(dict.fromkeys(selected_tools))

        return {
            "selected_tools": selected_tools,
            "question_type": question_type,
            "decision_reasoning": reasons,
            "tool_count": len(selected_tools)
        }