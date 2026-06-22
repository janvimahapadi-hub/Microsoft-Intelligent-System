from datetime import datetime
from intelligence.strategic_analyzer import StrategicAnalyzer


class CEOBriefing:
    """
    Formats StrategicAnalyzer output into a CEO-ready briefing report.
    StrategicAnalyzer = AI brain.
    CEOBriefing = report formatter.
    """

    def __init__(self, company_name="Microsoft"):
        self.company_name = company_name
        self.analyzer = StrategicAnalyzer(company_name=company_name)

    def generate(self, strategic_question, top_k=5, mode="fast"):
        result = self.analyzer.analyze(
            strategic_question=strategic_question,
            top_k=top_k,
            mode=mode
        )

        return self.format_report(result)

    def format_report(self, result):
        evidence = result.get("evidence", [])

        sources = sorted(
            set(item.get("source", "Unknown source") for item in evidence)
        )

        source_types = sorted(
            set(item.get("source_type", "unknown") for item in evidence)
        )

        return {
            "company": result.get("company", self.company_name),
            "question": result.get("question", ""),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "briefing": result.get("answer", ""),
            "retrieval_confidence": result.get("retrieval_confidence", 0.0),
            "llm_status": result.get("llm_status", ""),
            "evidence_count": len(evidence),
            "sources": sources,
            "source_types": source_types,
            "evidence": evidence,
        }

    def generate_markdown_report(self, report):
        evidence_lines = []

        for item in report.get("evidence", []):
            title = item.get("title", "Untitled")
            source = item.get("source", "Unknown source")
            published = item.get("published", "")
            url = item.get("url", "")

            if url:
                evidence_lines.append(
                    f"- **{title}** — {source} ({published})\n  {url}"
                )
            else:
                evidence_lines.append(
                    f"- **{title}** — {source} ({published})"
                )

        evidence_text = "\n".join(evidence_lines)

        return f"""
# CEO Strategic Briefing

**Company:** {report.get("company", "")}  
**Generated at:** {report.get("generated_at", "")}  
**Strategic question:** {report.get("question", "")}  

---

## Briefing

{report.get("briefing", "")}

---

## Retrieval Quality

**Retrieval confidence:** {report.get("retrieval_confidence", 0.0)}  
**Evidence count:** {report.get("evidence_count", 0)}  
**Sources used:** {", ".join(report.get("sources", []))}  
**Source types:** {", ".join(report.get("source_types", []))}  
**LLM status:** {report.get("llm_status", "")}

---

## Evidence Sources

{evidence_text}
""".strip()