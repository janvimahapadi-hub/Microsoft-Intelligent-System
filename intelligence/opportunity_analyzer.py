from collections import Counter

from utils.data_loader import get_normalized_documents


OPPORTUNITY_THEMES = {
    "AI Product Expansion": [
        "ai",
        "artificial intelligence",
        "copilot",
        "agent",
        "agents",
        "foundry",
        "model",
        "automation",
        "intelligent"
    ],
    "Cloud Growth": [
        "azure",
        "cloud",
        "infrastructure",
        "platform",
        "migration",
        "enterprise cloud",
        "hybrid cloud"
    ],
    "Security Differentiation": [
        "security",
        "defender",
        "entra",
        "identity",
        "threat",
        "governance",
        "compliance",
        "trust"
    ],
    "Developer Ecosystem": [
        "github",
        "developer",
        "developers",
        "open source",
        "devops",
        "code",
        "api",
        "sdk"
    ],
    "Partner Ecosystem": [
        "partner",
        "partners",
        "ecosystem",
        "customers",
        "enterprise",
        "transformation",
        "adoption"
    ],
    "Productivity and Microsoft 365": [
        "microsoft 365",
        "office",
        "teams",
        "outlook",
        "productivity",
        "collaboration",
        "workplace"
    ],
    "Windows and Devices": [
        "windows",
        "pc",
        "device",
        "devices",
        "surface",
        "operating system"
    ],
    "Gaming and Consumer": [
        "xbox",
        "gaming",
        "game pass",
        "activision",
        "minecraft",
        "consumer"
    ]
}


OPPORTUNITY_KEYWORDS = [
    "opportunity",
    "growth",
    "adoption",
    "customers",
    "enterprise",
    "scale",
    "scalable",
    "productivity",
    "innovation",
    "transformation",
    "partner",
    "platform",
    "revenue",
    "available",
    "launch",
    "new",
    "expand",
    "accelerate",
    "improve",
    "enable"
]


IMPACT_KEYWORDS_HIGH = [
    "enterprise",
    "revenue",
    "global",
    "scale",
    "fortune 500",
    "customers",
    "platform",
    "strategic",
    "production",
    "adoption"
]


IMPACT_KEYWORDS_MEDIUM = [
    "preview",
    "developer",
    "partner",
    "workflow",
    "productivity",
    "integration",
    "automation"
]


def combined_text(document):
    return f"{document.get('title', '')} {document.get('text', '')}".lower()


def keyword_count(text, keywords):
    text = text.lower()

    count = 0

    for keyword in keywords:
        if keyword.lower() in text:
            count += 1

    return count


def detect_theme(document):
    text = combined_text(document)

    theme_scores = {}

    for theme, keywords in OPPORTUNITY_THEMES.items():
        score = keyword_count(text, keywords)
        if score > 0:
            theme_scores[theme] = score

    if not theme_scores:
        return "General Opportunity", 0

    best_theme = max(
        theme_scores,
        key=theme_scores.get
    )

    return best_theme, theme_scores[best_theme]


def calculate_opportunity_score(document):
    text = combined_text(document)

    opportunity_score = keyword_count(text, OPPORTUNITY_KEYWORDS) * 2
    high_impact_score = keyword_count(text, IMPACT_KEYWORDS_HIGH) * 2
    medium_impact_score = keyword_count(text, IMPACT_KEYWORDS_MEDIUM)

    theme, theme_score = detect_theme(document)

    total_score = (
        opportunity_score
        + high_impact_score
        + medium_impact_score
        + theme_score
    )

    return total_score, theme


def calculate_impact_level(score):
    if score >= 12:
        return "High"

    if score >= 6:
        return "Medium"

    return "Low"


def calculate_confidence(document, score):
    confidence = 0.35

    text = combined_text(document)

    if score >= 6:
        confidence += 0.2

    if score >= 12:
        confidence += 0.15

    if document.get("url"):
        confidence += 0.1

    if document.get("source") and document.get("source") != "Unknown source":
        confidence += 0.1

    if document.get("published"):
        confidence += 0.1

    if keyword_count(text, OPPORTUNITY_KEYWORDS) >= 3:
        confidence += 0.1

    return min(round(confidence, 2), 1.0)


def create_opportunity(document):
    score, theme = calculate_opportunity_score(document)

    impact_level = calculate_impact_level(score)

    confidence = calculate_confidence(
        document=document,
        score=score
    )

    text = document.get("text", "")

    return {
        "title": theme,
        "opportunity_title": document.get("title", "Untitled opportunity"),
        "impact_level": impact_level,
        "confidence": confidence,
        "score": score,
        "source": document.get("source", "Unknown source"),
        "source_type": document.get("source_type", "unknown"),
        "published": document.get("published", ""),
        "url": document.get("url", ""),
        "evidence": text[:900],
        "strategic_rationale": build_rationale(theme, impact_level)
    }


def build_rationale(theme, impact_level):
    rationales = {
        "AI Product Expansion": (
            "Microsoft can expand AI-enabled products and services by converting AI interest into production-grade enterprise adoption."
        ),
        "Cloud Growth": (
            "Microsoft can strengthen Azure growth by positioning cloud infrastructure as the foundation for enterprise AI and digital transformation."
        ),
        "Security Differentiation": (
            "Microsoft can use security, identity, and compliance capabilities as a strategic differentiator for enterprise customers."
        ),
        "Developer Ecosystem": (
            "Microsoft can increase platform stickiness by using GitHub and developer tools as channels for AI and cloud adoption."
        ),
        "Partner Ecosystem": (
            "Microsoft can scale adoption faster by enabling partners to deliver repeatable solutions across industries."
        ),
        "Productivity and Microsoft 365": (
            "Microsoft can deepen enterprise productivity adoption by embedding intelligence into daily workplace tools."
        ),
        "Windows and Devices": (
            "Microsoft can improve user and enterprise value by connecting Windows, devices, AI, and security experiences."
        ),
        "Gaming and Consumer": (
            "Microsoft can strengthen consumer engagement through gaming, subscription services, and cross-platform ecosystems."
        ),
        "General Opportunity": (
            "The evidence suggests a possible strategic opportunity, but the theme requires more supporting data."
        )
    }

    return f"{rationales.get(theme, rationales['General Opportunity'])} Estimated impact level: {impact_level}."


def get_opportunities(topic="", limit=10):
    documents = get_normalized_documents()

    opportunities = []

    for document in documents:
        text = combined_text(document)

        if topic and topic.strip():
            topic_words = [
                word.lower().strip()
                for word in topic.replace(",", " ").split()
                if len(word.strip()) > 2
            ]

            if not any(word in text for word in topic_words):
                continue

        score, _ = calculate_opportunity_score(document)

        if score <= 0:
            continue

        opportunity = create_opportunity(document)
        opportunities.append(opportunity)

    opportunities = sorted(
        opportunities,
        key=lambda x: (
            x["score"],
            x["confidence"]
        ),
        reverse=True
    )

    return opportunities[:limit]


def get_opportunity_summary(topic="", limit=20):
    opportunities = get_opportunities(
        topic=topic,
        limit=limit
    )

    impact_counter = Counter(
        opportunity["impact_level"]
        for opportunity in opportunities
    )

    theme_counter = Counter(
        opportunity["title"]
        for opportunity in opportunities
    )

    return {
        "opportunities": opportunities,
        "impact_counter": impact_counter,
        "theme_counter": theme_counter,
        "total_opportunities": len(opportunities)
    }


if __name__ == "__main__":
    summary = get_opportunity_summary(
        topic="AI Copilot cloud security",
        limit=10
    )

    print("Total opportunities:", summary["total_opportunities"])
    print("Impact levels:", summary["impact_counter"])
    print("Themes:", summary["theme_counter"])

    for opportunity in summary["opportunities"][:5]:
        print("-" * 80)
        print("Theme:", opportunity["title"])
        print("Opportunity:", opportunity["opportunity_title"])
        print("Impact:", opportunity["impact_level"])
        print("Confidence:", opportunity["confidence"])
        print("Source:", opportunity["source"])