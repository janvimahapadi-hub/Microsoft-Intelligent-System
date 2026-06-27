from datetime import datetime


class MemoryAgent:
    """
    Memory Agent:
    Stores short-term session memory for the current strategic conversation.

    This supports follow-up questions and demonstrates memory capability.
    """

    def __init__(self):
        self.memory = []

    def save_interaction(
        self,
        user_goal,
        plan,
        tool_decision,
        validation,
        evidence_items,
        answer=None
    ):
        evidence_titles = [
            item.get("title", "Unknown evidence")
            for item in evidence_items
        ]

        memory_item = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_goal": user_goal,
            "plan": plan,
            "selected_tools": tool_decision.get("selected_tools", []),
            "validation_status": validation.get("validation_status", "Unknown"),
            "confidence": validation.get("confidence", 0.0),
            "evidence_titles": evidence_titles,
            "answer": answer
        }

        self.memory.append(memory_item)
        return memory_item

    def update_latest_answer(self, answer):
        """
        Updates the latest memory item with the final generated CEO briefing.
        """
        if not self.memory:
            return None

        self.memory[-1]["answer"] = answer
        return self.memory[-1]

    def get_recent_memory(self, limit=3):
        return self.memory[-limit:]

    def build_memory_context(self, limit=3):
        recent_items = self.get_recent_memory(limit=limit)

        if not recent_items:
            return "No previous memory available."

        memory_text = ""

        for index, item in enumerate(recent_items, start=1):
            memory_text += f"""
Memory {index}
Time: {item.get("timestamp")}
Previous Goal: {item.get("user_goal")}
Selected Tools: {", ".join(item.get("selected_tools", []))}
Validation: {item.get("validation_status")}
Confidence: {item.get("confidence")}
Evidence Used: {", ".join(item.get("evidence_titles", []))}
Answer Summary: {item.get("answer", "Not generated yet")[:500] if item.get("answer") else "Not generated yet"}
"""

        return memory_text.strip()

    def clear_memory(self):
        self.memory = []