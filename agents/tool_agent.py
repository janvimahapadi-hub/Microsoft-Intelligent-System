class ToolAgent:
    """
    Tool Agent:
    Selects which intelligence tools should be used based on the plan.
    This demonstrates autonomous tool selection.
    """

    def select_tools(self, plan):
        goal = plan.get("goal", "").lower()
        question_type = plan.get("question_type", "general_strategy")

        tools = []

        if question_type == "competitor_strategy" or any(
            word in goal for word in ["competitor", "aws", "google", "openai", "nvidia"]
        ):
            tools.append("competitor_intelligence")

        if question_type == "risk_strategy" or any(
            word in goal for word in ["risk", "security", "threat", "governance", "compliance"]
        ):
            tools.append("risk_analysis")

        if question_type == "opportunity_strategy" or any(
            word in goal for word in ["opportunity", "growth", "investment", "prioritize"]
        ):
            tools.append("opportunity_analysis")

        if question_type == "market_strategy" or any(
            word in goal for word in ["market", "trend", "industry"]
        ):
            tools.append("market_intelligence")

        tools.append("hybrid_retrieval")

        tools = list(dict.fromkeys(tools))

        return {
            "selected_tools": tools,
            "reason": f"Tools selected based on detected question type: {question_type}"
        }