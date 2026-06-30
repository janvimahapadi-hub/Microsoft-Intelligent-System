import json
import re
from pathlib import Path

from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent
from agents.validation_agent import ValidationAgent
from agents.memory_agent import MemoryAgent
from retrieval.hybrid_retriever import HybridRetriever


SENTIMENT_RESULTS_PATH = Path("data/sentiment_results.json")


class StrategicAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.tool_agent = ToolAgent()
        self.validation_agent = ValidationAgent()
        self.memory_agent = MemoryAgent()
        self.retriever = HybridRetriever()

    def load_sentiment_results(self):
        if not SENTIMENT_RESULTS_PATH.exists():
            return []

        try:
            with open(SENTIMENT_RESULTS_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []

    def normalize_key(self, value):
        if not value:
            return ""
        return " ".join(str(value).lower().strip().split())

    def build_sentiment_lookup(self, sentiment_data):
        lookup = {}

        for row in sentiment_data:
            url_key = self.normalize_key(row.get("url", ""))
            title_key = self.normalize_key(row.get("title", ""))

            if url_key:
                lookup[("url", url_key)] = row

            if title_key:
                lookup[("title", title_key)] = row

        return lookup

    def find_sentiment_match(self, item, sentiment_lookup):
        url_key = self.normalize_key(item.get("url", ""))
        title_key = self.normalize_key(item.get("title", ""))

        if url_key and ("url", url_key) in sentiment_lookup:
            return sentiment_lookup[("url", url_key)]

        if title_key and ("title", title_key) in sentiment_lookup:
            return sentiment_lookup[("title", title_key)]

        return None

    def build_signal_item(self, item):
        return {
            "title": item.get("title", "Unknown title"),
            "source": item.get("source", "Unknown source"),
            "source_type": item.get("source_type", "unknown"),
            "company": item.get("company", item.get("competitor", "Unknown")),
            "competitor": item.get("competitor", ""),
            "topic": item.get("agent_topic", "Unknown"),
            "sentiment": item.get("agent_sentiment", "Unknown"),
            "strategic_signal": item.get("agent_strategic_signal", "Unknown"),
            "url": item.get("url", ""),
            "evidence_preview": item.get("evidence", item.get("chunk_text", ""))[:250]
        }

    def extract_keywords_from_goal(self, goal):
        stop_words = {
            "what", "how", "why", "should", "could", "would", "the", "a", "an",
            "and", "or", "to", "in", "of", "for", "with", "on", "is", "are",
            "be", "by", "from", "as", "at", "this", "that", "which"
        }

        words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]+", goal.lower())

        keywords = [
            word for word in words
            if word not in stop_words and len(word) > 2
        ]

        return list(dict.fromkeys(keywords))

    def build_retrieval_queries(self, goal, selected_tools):
        keywords = self.extract_keywords_from_goal(goal)
        keyword_text = " ".join(keywords)

        queries = [goal]

        tool_query_templates = {
            "competitor_intelligence": [
                f"{goal} competitor strategy competitive positioning",
                f"{keyword_text} competition market positioning"
            ],
            "risk_analysis": [
                f"{goal} risks threats governance compliance security",
                f"{keyword_text} risk governance compliance"
            ],
            "opportunity_analysis": [
                f"{goal} opportunities growth investment adoption",
                f"{keyword_text} opportunity growth adoption"
            ],
            "market_intelligence": [
                f"{goal} market trends industry adoption demand",
                f"{keyword_text} market trends industry"
            ],
            "hybrid_retrieval": [
                f"{goal} evidence strategic intelligence"
            ]
        }

        for tool in selected_tools:
            queries.extend(tool_query_templates.get(tool, []))

        clean_queries = []

        for query in queries:
            query = " ".join(query.split())

            if query and query not in clean_queries:
                clean_queries.append(query)

        return clean_queries

    def retrieve_evidence(self, goal, selected_tools, top_k=5):
        queries = self.build_retrieval_queries(
            goal=goal,
            selected_tools=selected_tools
        )

        all_results = []

        for query in queries:
            try:
                results = self.retriever.search(query, top_k=3)
                all_results.extend(results)
            except Exception:
                continue

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

        final_evidence = unique_results[:top_k]

        return {
            "queries_used": queries,
            "evidence": final_evidence,
            "retrieval_count": len(final_evidence)
        }

    def analyze_with_existing_tools(self, goal, evidence_items, selected_tools):
        sentiment_data = self.load_sentiment_results()
        sentiment_lookup = self.build_sentiment_lookup(sentiment_data)

        risk_count = 0
        opportunity_count = 0
        neutral_count = 0
        irrelevant_count = 0
        matched_sentiment_items = 0
        competitor_count = 0
        market_count = 0

        risk_items = []
        opportunity_items = []
        competitor_items = []
        market_items = []

        topics = {}
        sentiments = {}
        analyzed_evidence = []

        for item in evidence_items:
            matched_row = self.find_sentiment_match(item, sentiment_lookup)

            if matched_row:
                matched_sentiment_items += 1

                strategic_signal = matched_row.get("strategic_signal", "Neutral")
                sentiment = matched_row.get("sentiment", "Unknown")
                topic = matched_row.get("topic", "Unknown")

                item["agent_strategic_signal"] = strategic_signal
                item["agent_sentiment"] = sentiment
                item["agent_topic"] = topic
                item["analysis_source"] = "sentiment_results.json"

                if strategic_signal == "Risk":
                    risk_count += 1
                    risk_items.append(self.build_signal_item(item))
                elif strategic_signal == "Opportunity":
                    opportunity_count += 1
                    opportunity_items.append(self.build_signal_item(item))
                elif strategic_signal == "Irrelevant":
                    irrelevant_count += 1
                else:
                    neutral_count += 1

                topics[topic] = topics.get(topic, 0) + 1
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1

            else:
                text = " ".join([
                    str(item.get("title", "")),
                    str(item.get("source", "")),
                    str(item.get("evidence", "")),
                    str(item.get("chunk_text", "")),
                    str(item.get("text", ""))
                ]).lower()

                item["analysis_source"] = "fallback_keyword_scan"
                item["agent_sentiment"] = "Unknown"
                item["agent_topic"] = "Unknown"

                if any(word in text for word in [
                    "risk", "security", "threat", "governance",
                    "compliance", "vulnerability"
                ]):
                    risk_count += 1
                    item["agent_strategic_signal"] = "Risk"
                    risk_items.append(self.build_signal_item(item))

                elif any(word in text for word in [
                    "opportunity", "growth", "adoption",
                    "enterprise", "investment", "scale"
                ]):
                    opportunity_count += 1
                    item["agent_strategic_signal"] = "Opportunity"
                    opportunity_items.append(self.build_signal_item(item))

                else:
                    neutral_count += 1
                    item["agent_strategic_signal"] = "Neutral"

            text_for_context = " ".join([
                str(item.get("title", "")),
                str(item.get("source", "")),
                str(item.get("evidence", "")),
                str(item.get("chunk_text", "")),
                str(item.get("text", ""))
            ]).lower()

            company = str(item.get("company", "")).lower()
            competitor = str(item.get("competitor", "")).lower()
            source_type = str(item.get("source_type", "")).lower()

            is_competitor_item = (
                competitor
                or source_type == "competitor"
                or (company and company != "microsoft")
                or any(word in text_for_context for word in [
                    "competitor", "competition", "rival", "compete", "competitive"
                ])
            )

            if is_competitor_item:
                competitor_count += 1
                competitor_items.append(self.build_signal_item(item))

            is_market_item = any(word in text_for_context for word in [
                "market", "trend", "industry", "adoption", "demand"
            ])

            if is_market_item:
                market_count += 1
                market_items.append(self.build_signal_item(item))

            analyzed_evidence.append(item)

        dashboard_risks = sum(
            1 for row in sentiment_data
            if row.get("strategic_signal") == "Risk"
        )

        dashboard_opportunities = sum(
            1 for row in sentiment_data
            if row.get("strategic_signal") == "Opportunity"
        )

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
            "neutral_count": neutral_count,
            "irrelevant_count": irrelevant_count,
            "competitor_count": competitor_count,
            "market_count": market_count,
            "risk_items": risk_items,
            "opportunity_items": opportunity_items,
            "competitor_items": competitor_items,
            "market_items": market_items,
            "matched_sentiment_items": matched_sentiment_items,
            "total_evidence_items": len(evidence_items),
            "topics_in_retrieved_evidence": topics,
            "sentiments_in_retrieved_evidence": sentiments,
            "dashboard_risk_signals": dashboard_risks,
            "dashboard_opportunity_signals": dashboard_opportunities,
            "analyzed_evidence": analyzed_evidence,
            "analysis_summary": {
                "dominant_signal": dominant_signal,
                "has_competitor_context": competitor_count > 0,
                "has_market_context": market_count > 0,
                "analysis_method": (
                    "Matched retrieved evidence with sentiment_results.json; "
                    "fallback keyword scan used only when no match was found."
                )
            }
        }

    def build_decision(self, tool_decision, validation):
        selected_tools = tool_decision.get("selected_tools", [])
        confidence = validation.get("confidence", 0.0)
        ready = validation.get("is_ready_for_recommendation", False)
        warnings = validation.get("warnings", [])

        if ready:
            decision_status = "Recommendation approved for presentation"
        else:
            decision_status = (
                "Recommendation requires caution because validation confidence is weak"
            )

        return {
            "selected_tools": selected_tools,
            "tool_selection_reason": tool_decision.get(
                "decision_reasoning",
                ["Tools selected based on agent planning."]
            ),
            "validation_status": validation.get("validation_status", "Unknown"),
            "confidence": confidence,
            "ready_for_recommendation": ready,
            "decision_status": decision_status,
            "warnings": warnings
        }

    def execute(self, user_goal, top_k=5):
        plan = self.planner.create_plan(user_goal)

        tool_decision = self.tool_agent.select_tools(plan)
        selected_tools = tool_decision.get("selected_tools", [])

        retrieved_data = self.retrieve_evidence(
            goal=user_goal,
            selected_tools=selected_tools,
            top_k=top_k
        )

        evidence_items = retrieved_data.get("evidence", [])

        analysis = self.analyze_with_existing_tools(
            goal=user_goal,
            evidence_items=evidence_items,
            selected_tools=selected_tools
        )

        validation = self.validation_agent.validate(
            goal=user_goal,
            plan=plan,
            tool_decision=tool_decision,
            retrieved_data=retrieved_data,
            analysis_result=analysis
        )

        decision = self.build_decision(
            tool_decision=tool_decision,
            validation=validation
        )

        memory = self.memory_agent.save_interaction(
            user_goal=user_goal,
            plan=plan,
            tool_decision=tool_decision,
            validation=validation,
            evidence_items=evidence_items,
            answer=None
        )

        return {
            "goal": user_goal,
            "workflow": [
                "Goal received",
                "Plan created by PlannerAgent",
                "Tools selected autonomously by ToolAgent",
                "Dynamic retrieval queries created",
                "Evidence retrieved using HybridRetriever",
                "Retrieved evidence matched with sentiment_results.json where possible",
                "Risks, opportunities, topics, and sentiments analyzed",
                "Recommendation validated by ValidationAgent",
                "Agent decision created",
                "Interaction stored in MemoryAgent"
            ],
            "plan": plan,
            "tool_decision": tool_decision,
            "retrieval": retrieved_data,
            "analysis": analysis,
            "validation": validation,
            "decision": decision,
            "memory": memory,
            "memory_context": self.memory_agent.build_memory_context(),
            "evidence": evidence_items,
            "confidence": validation.get("confidence", 0.0),
            "ready": validation.get("is_ready_for_recommendation", False)
        }