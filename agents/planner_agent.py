class PlannerAgent:
    """
    Planner Agent:
    Converts the user's strategic goal into a clear execution plan.
    This demonstrates planning before retrieval and generation.
    """

    def create_plan(self, user_goal):
        goal_lower = user_goal.lower()

        plan = {
            "goal": user_goal,
            "question_type": "general_strategy",
            "steps": []
        }

        if any(word in goal_lower for word in ["competitor", "aws", "google", "openai", "nvidia"]):
            plan["question_type"] = "competitor_strategy"
            plan["steps"].append("Analyze competitor activity and positioning")

        if any(word in goal_lower for word in ["risk", "security", "threat", "governance", "compliance"]):
            plan["question_type"] = "risk_strategy"
            plan["steps"].append("Analyze strategic and security risks")

        if any(word in goal_lower for word in ["opportunity", "growth", "investment", "prioritize"]):
            plan["question_type"] = "opportunity_strategy"
            plan["steps"].append("Analyze opportunity signals and investment areas")

        if any(word in goal_lower for word in ["market", "trend", "industry"]):
            plan["question_type"] = "market_strategy"
            plan["steps"].append("Analyze market trends and external signals")

        if not plan["steps"]:
            plan["steps"].append("Retrieve general strategic evidence")

        plan["steps"].extend([
            "Retrieve relevant evidence using hybrid retrieval",
            "Analyze risks, opportunities, competitors, and market signals",
            "Generate evidence-based CEO recommendation",
            "Validate recommendation before presenting final output"
        ])

        return plan