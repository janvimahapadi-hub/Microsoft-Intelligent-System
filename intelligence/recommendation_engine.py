from collections import Counter

from intelligence.opportunity_analyzer import get_opportunities
from intelligence.risk_analyzer import get_risks
from sentiment.sentiment_analyzer import get_sentiment_analysis


THEME_ACTIONS = {
    "AI Product Expansion": {
        "recommendation": "Scale production-ready AI solutions through Copilot, Foundry, and enterprise workflows",
        "owners": ["Product", "Azure", "Microsoft 365", "Sales", "Compliance"],
        "kpis": [
            "Number of production AI deployments",
            "Copilot or agent adoption rate",
            "Customer ROI from AI-enabled workflows"
        ]
    },
    "Cloud Growth": {
        "recommendation": "Use Azure as the execution platform for enterprise AI and cloud transformation",
        "owners": ["Azure", "Cloud Infrastructure", "Enterprise Sales", "Partner Team"],
        "kpis": [
            "Azure AI workload growth",
            "Enterprise cloud migration pipeline",
            "Customer retention in strategic cloud accounts"
        ]
    },
    "Security Differentiation": {
        "recommendation": "Differentiate Microsoft through integrated AI security, identity, and compliance capabilities",
        "owners": ["Security", "Identity", "Compliance", "Customer Success"],
        "kpis": [
            "Security product adoption",
            "Threat detection and response improvement",
            "Enterprise trust and compliance wins"
        ]
    },
    "Developer Ecosystem": {
        "recommendation": "Strengthen developer adoption through GitHub, tools, APIs, and AI-assisted software workflows",
        "owners": ["GitHub", "Developer Relations", "Azure", "Product Engineering"],
        "kpis": [
            "Developer activation rate",
            "GitHub Copilot usage",
            "Platform integration growth"
        ]
    },
    "Partner Ecosystem": {
        "recommendation": "Accelerate partner-led transformation to scale Microsoft solutions across industries",
        "owners": ["Partner Team", "Sales", "Industry Solutions", "Customer Success"],
        "kpis": [
            "Partner-led customer deployments",
            "Partner pipeline growth",
            "Repeatable industry solution adoption"
        ]
    },
    "Productivity and Microsoft 365": {
        "recommendation": "Deepen Microsoft 365 value by embedding AI into daily productivity and collaboration workflows",
        "owners": ["Microsoft 365", "Teams", "Copilot", "Enterprise Sales"],
        "kpis": [
            "Microsoft 365 Copilot usage",
            "Workflow productivity improvement",
            "Enterprise seat expansion"
        ]
    },
    "Windows and Devices": {
        "recommendation": "Position Windows and devices as trusted AI-enabled productivity endpoints",
        "owners": ["Windows", "Devices", "Security", "Enterprise Sales"],
        "kpis": [
            "Windows AI feature adoption",
            "Enterprise device engagement",
            "Security-driven upgrade demand"
        ]
    },
    "Gaming and Consumer": {
        "recommendation": "Expand consumer engagement through gaming, subscriptions, and cross-platform services",
        "owners": ["Xbox", "Gaming", "Consumer Marketing", "Cloud Gaming"],
        "kpis": [
            "Game Pass subscriber growth",
            "Monthly active users",
            "Cross-platform engagement"
        ]
    },
    "General Opportunity": {
        "recommendation": "Investigate the opportunity through a focused evidence-backed validation sprint",
        "owners": ["Strategy", "Product", "Market Intelligence"],
        "kpis": [
            "Evidence quality score",
            "Validated business use cases",
            "Pilot readiness"
        ]
    }
}


def get_theme_action(theme):
    return THEME_ACTIONS.get(
        theme,
        THEME_ACTIONS["General Opportunity"]
    )


def priority_from_impact(impact_level):
    if impact_level == "High":
        return "High"

    if impact_level == "Medium":
        return "Medium"

    return "Low"


def risk_weight(severity):
    if severity == "High":
        return 1.0

    if severity == "Medium":
        return 0.6

    if severity == "Low":
        return 0.3

    return 0.2


def get_risk_level(related_risks):
    if not related_risks:
        return "Low"

    severities = [
        risk.get("severity_level", "Low")
        for risk in related_risks
    ]

    if "High" in severities:
        return "High"

    if "Medium" in severities:
        return "Medium"

    return "Low"


def text_contains_theme(text, theme):
    theme_words = [
        word.lower()
        for word in theme.replace("&", " ").replace("/", " ").split()
        if len(word) > 2
    ]

    text = text.lower()

    return any(word in text for word in theme_words)


def find_related_risks(opportunity, risks, max_risks=3):
    theme = opportunity.get("title", "")
    opportunity_text = (
        f"{opportunity.get('opportunity_title', '')} "
        f"{opportunity.get('evidence', '')} "
        f"{theme}"
    ).lower()

    related = []

    for risk in risks:
        risk_text = (
            f"{risk.get('risk_title', '')} "
            f"{risk.get('risk_category', '')} "
            f"{risk.get('evidence', '')}"
        ).lower()

        is_related = False

        if text_contains_theme(risk_text, theme):
            is_related = True

        opportunity_words = [
            word
            for word in opportunity_text.split()
            if len(word) > 4
        ]

        shared_words = [
            word
            for word in opportunity_words
            if word in risk_text
        ]

        if len(shared_words) >= 2:
            is_related = True

        if is_related:
            related.append(risk)

    if not related:
        related = risks[:max_risks]

    related = sorted(
        related,
        key=lambda x: (
            risk_weight(x.get("severity_level", "Low")),
            x.get("confidence", 0.0)
        ),
        reverse=True
    )

    return related[:max_risks]


def build_expected_impact(theme, impact_level):
    if theme == "AI Product Expansion":
        return (
            "Higher enterprise AI adoption, stronger product differentiation, and more measurable customer productivity outcomes."
        )

    if theme == "Cloud Growth":
        return (
            "Stronger Azure workload growth, deeper enterprise cloud dependency, and improved cloud platform positioning."
        )

    if theme == "Security Differentiation":
        return (
            "Improved enterprise trust, stronger security-led selling, and better positioning in regulated industries."
        )

    if theme == "Developer Ecosystem":
        return (
            "Increased developer loyalty, stronger platform stickiness, and faster adoption of Microsoft tools and APIs."
        )

    if theme == "Partner Ecosystem":
        return (
            "Faster market reach through partners, repeatable industry deployments, and larger enterprise transformation pipeline."
        )

    if theme == "Productivity and Microsoft 365":
        return (
            "Higher Microsoft 365 engagement, stronger seat expansion, and clearer ROI from AI-assisted work."
        )

    if theme == "Windows and Devices":
        return (
            "Improved Windows relevance, stronger enterprise upgrade value, and tighter connection between device, AI, and security experiences."
        )

    if theme == "Gaming and Consumer":
        return (
            "Higher consumer engagement, stronger subscription value, and better cross-platform ecosystem growth."
        )

    return (
        f"Potential {impact_level.lower()} strategic impact if validated through stronger evidence and execution planning."
    )


def build_execution_plan(theme):
    if theme == "AI Product Expansion":
        return [
            "First 30 days: Identify 3 high-value enterprise AI workflows with measurable ROI.",
            "Days 31-60: Run pilots with selected customers or internal business units.",
            "Days 61-90: Convert successful pilots into repeatable deployment playbooks."
        ]

    if theme == "Cloud Growth":
        return [
            "First 30 days: Map AI and cloud workloads with strongest Azure fit.",
            "Days 31-60: Package Azure-based migration and AI deployment offers.",
            "Days 61-90: Track pipeline conversion and scale through sales and partners."
        ]

    if theme == "Security Differentiation":
        return [
            "First 30 days: Identify top security risks and customer trust requirements.",
            "Days 31-60: Integrate security, identity, and governance messaging into offers.",
            "Days 61-90: Measure security-led adoption and customer risk reduction."
        ]

    if theme == "Developer Ecosystem":
        return [
            "First 30 days: Identify developer workflows with high AI or automation demand.",
            "Days 31-60: Improve documentation, tooling, and GitHub-based activation.",
            "Days 61-90: Measure developer usage, retention, and integration depth."
        ]

    if theme == "Partner Ecosystem":
        return [
            "First 30 days: Select partner segments with repeatable customer demand.",
            "Days 31-60: Build partner enablement materials and solution templates.",
            "Days 61-90: Track partner-led deployments and pipeline growth."
        ]

    return [
        "First 30 days: Validate the opportunity with evidence and stakeholder interviews.",
        "Days 31-60: Run a focused pilot with clear owners and KPIs.",
        "Days 61-90: Decide whether to scale, revise, or stop based on measured outcomes."
    ]


def build_risk_assessment(related_risks):
    if not related_risks:
        return (
            "No major related risks were detected in the current evidence set, but additional market and competitor evidence is recommended."
        )

    top_risk = related_risks[0]

    return (
        f"Primary risk: {top_risk.get('risk_category', 'General Strategic Risk')}. "
        f"Severity: {top_risk.get('severity_level', 'Unknown')}. "
        f"Mitigation: {top_risk.get('mitigation', 'Assign ownership and monitor leading indicators.')}"
    )


def calculate_recommendation_confidence(opportunity, related_risks, sentiment_average):
    confidence = 0.35

    confidence += opportunity.get("confidence", 0.0) * 0.35

    if opportunity.get("url"):
        confidence += 0.05

    if opportunity.get("source"):
        confidence += 0.05

    if related_risks:
        confidence += 0.1

    if sentiment_average >= 0:
        confidence += 0.05

    if opportunity.get("impact_level") == "High":
        confidence += 0.05

    return min(round(confidence, 2), 1.0)


def create_recommendation(opportunity, risks, sentiment_average):
    theme = opportunity.get("title", "General Opportunity")
    action_config = get_theme_action(theme)

    related_risks = find_related_risks(
        opportunity=opportunity,
        risks=risks,
        max_risks=3
    )

    risk_level = get_risk_level(related_risks)
    priority = priority_from_impact(
        opportunity.get("impact_level", "Low")
    )

    confidence = calculate_recommendation_confidence(
        opportunity=opportunity,
        related_risks=related_risks,
        sentiment_average=sentiment_average
    )

    recommendation = {
        "theme": theme,
        "recommendation": action_config["recommendation"],
        "priority": priority,
        "confidence": confidence,
        "expected_impact": build_expected_impact(
            theme=theme,
            impact_level=opportunity.get("impact_level", "Low")
        ),
        "risk_level": risk_level,
        "risk_assessment": build_risk_assessment(related_risks),
        "execution_plan": build_execution_plan(theme),
        "owners": action_config["owners"],
        "kpis": action_config["kpis"],
        "source_opportunity": opportunity,
        "related_risks": related_risks,
        "sentiment_average": sentiment_average,
        "evidence": [
            {
                "title": opportunity.get("opportunity_title", "Untitled evidence"),
                "source": opportunity.get("source", "Unknown source"),
                "url": opportunity.get("url", ""),
                "summary": opportunity.get("evidence", "")[:350]
            }
        ]
    }

    return recommendation


def select_best_opportunities(opportunities, limit):
    """
    Prefer theme diversity so recommendations do not all come from the same category.
    """

    selected = []
    seen_themes = set()

    for opportunity in opportunities:
        theme = opportunity.get("title", "General Opportunity")

        if theme in seen_themes:
            continue

        selected.append(opportunity)
        seen_themes.add(theme)

        if len(selected) >= limit:
            return selected

    for opportunity in opportunities:
        if opportunity in selected:
            continue

        selected.append(opportunity)

        if len(selected) >= limit:
            break

    return selected


def get_strategic_recommendations(topic="", limit=5):
    opportunities = get_opportunities(
        topic=topic,
        limit=25
    )

    risks = get_risks(
        topic=topic,
        limit=20
    )

    sentiment_data = get_sentiment_analysis(
        topic=topic,
        limit=80
    )

    sentiment_average = sentiment_data.get("overall_average", 0.0)

    selected_opportunities = select_best_opportunities(
        opportunities=opportunities,
        limit=limit
    )

    recommendations = []

    for opportunity in selected_opportunities:
        recommendation = create_recommendation(
            opportunity=opportunity,
            risks=risks,
            sentiment_average=sentiment_average
        )

        recommendations.append(recommendation)

    priority_counter = Counter(
        item["priority"]
        for item in recommendations
    )

    risk_counter = Counter(
        item["risk_level"]
        for item in recommendations
    )

    theme_counter = Counter(
        item["theme"]
        for item in recommendations
    )

    average_confidence = 0.0

    if recommendations:
        average_confidence = round(
            sum(item["confidence"] for item in recommendations) / len(recommendations),
            2
        )

    return {
        "topic": topic,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "priority_counter": priority_counter,
        "risk_counter": risk_counter,
        "theme_counter": theme_counter,
        "average_confidence": average_confidence,
        "sentiment_average": sentiment_average
    }


if __name__ == "__main__":
    result = get_strategic_recommendations(
        topic="AI Copilot security",
        limit=5
    )

    print("Recommendations:", result["total_recommendations"])
    print("Priority:", result["priority_counter"])
    print("Risk:", result["risk_counter"])
    print("Average confidence:", result["average_confidence"])

    for rec in result["recommendations"]:
        print("-" * 80)
        print("Recommendation:", rec["recommendation"])
        print("Theme:", rec["theme"])
        print("Priority:", rec["priority"])
        print("Risk:", rec["risk_level"])
        print("Confidence:", rec["confidence"])