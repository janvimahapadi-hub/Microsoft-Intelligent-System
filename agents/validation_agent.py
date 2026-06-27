class ValidationAgent:
    """
    Validation Agent:
    Validates whether the recommendation is supported by enough evidence.
    This demonstrates recommendation validation before presenting the final answer.
    """

    def validate(self, goal, plan, tool_decision, retrieved_data, analysis_result):
        evidence_items = retrieved_data.get("evidence", [])
        selected_tools = tool_decision.get("selected_tools", [])

        evidence_count = len(evidence_items)

        sources = set()
        companies = set()
        urls = set()

        for item in evidence_items:
            source = item.get("source", "")
            company = item.get("company") or item.get("competitor") or item.get("source", "")
            url = item.get("url", "")

            if source:
                sources.add(source)

            if company:
                companies.add(company)

            if url:
                urls.add(url)

        confidence = 0.0

        confidence += min(evidence_count / 5, 1.0) * 0.30
        confidence += min(len(sources) / 3, 1.0) * 0.25
        confidence += min(len(companies) / 3, 1.0) * 0.25
        confidence += min(len(urls) / 5, 1.0) * 0.20

        confidence = round(min(confidence, 1.0), 2)

        warnings = []

        if evidence_count < 3:
            warnings.append("Low evidence count. Recommendation should be treated cautiously.")

        if len(sources) < 2:
            warnings.append("Evidence comes from limited source diversity.")

        if "competitor_intelligence" in selected_tools and len(companies) < 2:
            warnings.append("Competitor question detected, but competitor evidence is limited.")

        if analysis_result.get("risk_count", 0) == 0 and "risk_analysis" in selected_tools:
            warnings.append("Risk analysis was requested, but few risk signals were found.")

        if analysis_result.get("opportunity_count", 0) == 0 and "opportunity_analysis" in selected_tools:
            warnings.append("Opportunity analysis was requested, but few opportunity signals were found.")

        if confidence >= 0.75:
            validation_status = "Strong"
        elif confidence >= 0.50:
            validation_status = "Moderate"
        else:
            validation_status = "Weak"

        return {
            "validation_status": validation_status,
            "confidence": confidence,
            "evidence_count": evidence_count,
            "source_count": len(sources),
            "company_count": len(companies),
            "url_count": len(urls),
            "warnings": warnings,
            "is_ready_for_recommendation": confidence >= 0.50
        }