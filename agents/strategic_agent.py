import json
from pathlib import Path

from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.validation_agent import ValidationAgent
from agents.memory_agent import MemoryAgent
from retrieval.hybrid_retriever import HybridRetriever


SENTIMENT_RESULTS_PATH = Path("data/sentiment_results.json")


class StrategicAgent:
    """
    Strategic Agent / Orchestrator

    It controls:
    Goal → Plan → Tool Selection → Retrieval → Analysis → Validation → Memory

    It does not generate the final CEO briefing.
    The final LLM generation happens in StrategicAnalyzer through Ollama.
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.tool_agent = ToolAgent()
        self.validation_agent = ValidationAgent()
        self.memory_agent = MemoryAgent()

        # Existing project tool
        self.retriever = HybridRetriever()

    def load_sentiment_results(self):
        if not SENTIMENT_RESULTS_PATH.exists():
            return []

        with open(SENTIMENT_RESULTS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    def build_retrieval_queries(self, goal, selected_tools):
        queries = [goal]

        if "competitor_intelligence" in selected_tools:
            queries.extend([
                f"{goal} AWS Google Cloud OpenAI NVIDIA competitor strategy",
                "Microsoft competitors AI cloud infrastructure AWS Google Cloud OpenAI NVIDIA"
            ])

        if "risk_analysis" in selected_tools:
            queries.extend([
                f"{goal} risk security governance compliance threat",
                "Microsoft AI security risk governance compliance cloud"
            ])

        if "opportunity_analysis" in selected_tools:
            queries.extend([
                f"{goal} opportunity growth investment Azure Copilot Foundry",
                "Microsoft Azure AI Foundry Copilot enterprise opportunity"
            ])

        if "market_intelligence" in selected_tools:
            queries.extend([
                f"{goal} market trends enterprise AI cloud",
                "AI cloud market trends enterprise adoption Microsoft competitors"
            ])

        return list(dict.fromkeys(queries))

    def retrieve_evidence(self, goal, selected_tools, top_k=5):
        queries = self.build_retrieval_queries(
            goal=goal,
            selected_tools=selected_tools
        )

        all_results = []

        for query in queries:
            results = self.retriever.search(query, top_k=3)
            all_results.extend(results)

        unique_results = []
        seen = set()

        for item in all_results:
            key = item.get("url") or item.get("title") or str(item.get("chunk_id"))

            if key in seen:
                continue

            seen.add(key)
            unique_results.append(item)

        unique_results = sorted(
            unique_results,
            key=lambda x: x.get("score", 999999)
        )

        return {
            "queries_used": queries,
            "evidence": unique_results[:top_k],
            "retrieval_count": len(unique_results[:top_k])
        }

    def analyze_with_existing_tools(self, goal, evidence_items, selected_tools):
        sentiment_data = self.load_sentiment_results()

        risk_count = 0
        opportunity_count = 0
        competitor_count = 0
        market_count = 0

        for item in evidence_items:
            text = " ".join([
                item.get("title", ""),
                item.get("source", ""),
                item.get("evidence", "")
            ]).lower()

            if any(word in text for word in ["risk", "security", "threat", "governance", "compliance"]):
                risk_count += 1

            if any(word in text for word in ["opportunity", "growth", "azure", "copilot", "foundry", "enterprise"]):
                opportunity_count += 1

            if any(word in text for word in ["aws", "google", "openai", "nvidia", "anthropic"]):
                competitor_count += 1

            if any(word in text for word in ["market", "trend", "industry", "adoption"]):
                market_count += 1

        dashboard_risks = 0
        dashboard_opportunities = 0

        for row in sentiment_data:
            signal = row.get("strategic_signal", "")

            if signal == "Risk":
                dashboard_risks += 1

            if signal == "Opportunity":
                dashboard_opportunities += 1

        if risk_count > opportunity_count:
            dominant_signal = "Risk-focused"
        elif opportunity_count > risk_count:
            dominant_signal = "Opportunity-focused"
        else:
            dominant_signal = "Balanced"

        return {
            "goal": goal,
            "selected_tools_used": selected_tools,
            "risk_count": risk_count,
            "opportunity_count": opportunity_count,
            "competitor_count": competitor_count,
            "market_count": market_count,
            "dashboard_risk_signals": dashboard_risks,
            "dashboard_opportunity_signals": dashboard_opportunities,
            "analysis_summary": {
                "dominant_signal": dominant_signal,
                "has_competitor_context": competitor_count > 0,
                "has_market_context": market_count > 0
            }
        }

    def execute(self, user_goal, top_k=5):
        # Step 1: Planning
        plan = self.planner.create_plan(user_goal)

        # Step 2: Tool selection
        tool_decision = self.tool_agent.select_tools(plan)
        selected_tools = tool_decision.get("selected_tools", [])

        # Step 3: Retrieval using HybridRetriever tool
        retrieved_data = self.retrieve_evidence(
            goal=user_goal,
            selected_tools=selected_tools,
            top_k=top_k
        )

        # Step 4: Analysis using existing evidence + sentiment results
        analysis = self.analyze_with_existing_tools(
            goal=user_goal,
            evidence_items=retrieved_data.get("evidence", []),
            selected_tools=selected_tools
        )

        # Step 5: Validation
        validation = self.validation_agent.validate(
            goal=user_goal,
            plan=plan,
            tool_decision=tool_decision,
            retrieved_data=retrieved_data,
            analysis_result=analysis
        )

        # Step 6: Memory
        memory = self.memory_agent.save_interaction(
            user_goal=user_goal,
            plan=plan,
            tool_decision=tool_decision,
            validation=validation,
            evidence_items=retrieved_data.get("evidence", []),
            answer=None
        )

        return {
            "goal": user_goal,
            "plan": plan,
            "tool_decision": tool_decision,
            "retrieval": retrieved_data,
            "analysis": analysis,
            "validation": validation,
            "memory": memory,
            "memory_context": self.memory_agent.build_memory_context(),
            "evidence": retrieved_data.get("evidence", []),
            "confidence": validation.get("confidence", 0.0),
            "ready": validation.get("is_ready_for_recommendation", False)
        }