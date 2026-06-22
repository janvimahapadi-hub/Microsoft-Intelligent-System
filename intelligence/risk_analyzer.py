from collections import Counter

from utils.data_loader import get_normalized_documents


RISK_CATEGORIES = {
    "Cybersecurity Threat": [
        "security",
        "threat",
        "attack",
        "cyberattack",
        "ransomware",
        "phishing",
        "malware",
        "breach",
        "vulnerability",
        "defender",
        "identity",
        "entra"
    ],
    "AI Governance Risk": [
        "ai governance",
        "governance",
        "responsible ai",
        "trust",
        "safety",
        "compliance",
        "model risk",
        "hallucination",
        "data protection"
    ],
    "Regulatory and Compliance Risk": [
        "regulation",
        "regulatory",
        "compliance",
        "privacy",
        "law",
        "policy",
        "data protection",
        "risk management"
    ],
    "Competitive Pressure": [
        "competitor",
        "competition",
        "aws",
        "google",
        "google cloud",
        "nvidia",
        "apple",
        "meta",
        "anthropic",
        "oracle",
        "salesforce",
        "sap"
    ],
    "Product Adoption Risk": [
        "adoption",
        "customers",
        "user",
        "users",
        "experience",
        "cost",
        "quality",
        "deployment",
        "migration",
        "implementation"
    ],
    "Cloud and Infrastructure Risk": [
        "cloud",
        "azure",
        "infrastructure",
        "availability",
        "outage",
        "latency",
        "reliability",
        "scalability"
    ],
    "Reputation and Trust Risk": [
        "trust",
        "reputation",
        "concern",
        "criticism",
        "public",
        "sentiment",
        "customer confidence"
    ],
    "Partner and Ecosystem Risk": [
        "partner",
        "partners",
        "ecosystem",
        "dependency",
        "integration",
        "channel",
        "reseller"
    ]
}


GENERAL_RISK_KEYWORDS = [
    "risk",
    "threat",
    "challenge",
    "concern",
    "issue",
    "problem",
    "incident",
    "attack",
    "vulnerability",
    "regulation",
    "privacy",
    "compliance",
    "competition",
    "uncertainty",
    "cost",
    "delay",
    "failure",
    "slow",
    "trust"
]


HIGH_SEVERITY_KEYWORDS = [
    "attack",
    "breach",
    "cyberattack",
    "ransomware",
    "vulnerability",
    "regulation",
    "compliance",
    "privacy",
    "security",
    "critical",
    "failure",
    "outage",
    "threat"
]


MEDIUM_SEVERITY_KEYWORDS = [
    "competition",
    "cost",
    "adoption",
    "delay",
    "concern",
    "challenge",
    "quality",
    "migration",
    "dependency",
    "integration"
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


def detect_risk_category(document):
    text = combined_text(document)

    category_scores = {}

    for category, keywords in RISK_CATEGORIES.items():
        score = keyword_count(text, keywords)
        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return "General Strategic Risk", 0

    best_category = max(
        category_scores,
        key=category_scores.get
    )

    return best_category, category_scores[best_category]


def calculate_risk_score(document):
    text = combined_text(document)

    general_score = keyword_count(text, GENERAL_RISK_KEYWORDS) * 2
    high_score = keyword_count(text, HIGH_SEVERITY_KEYWORDS) * 3
    medium_score = keyword_count(text, MEDIUM_SEVERITY_KEYWORDS) * 2

    category, category_score = detect_risk_category(document)

    total_score = (
        general_score
        + high_score
        + medium_score
        + category_score
    )

    return total_score, category


def calculate_severity_level(score):
    if score >= 14:
        return "High"

    if score >= 7:
        return "Medium"

    return "Low"


def calculate_confidence(document, score):
    confidence = 0.35

    text = combined_text(document)

    if score >= 7:
        confidence += 0.2

    if score >= 14:
        confidence += 0.15

    if document.get("url"):
        confidence += 0.1

    if document.get("source") and document.get("source") != "Unknown source":
        confidence += 0.1

    if document.get("published"):
        confidence += 0.1

    if keyword_count(text, GENERAL_RISK_KEYWORDS) >= 3:
        confidence += 0.1

    return min(round(confidence, 2), 1.0)


def build_mitigation(category):
    mitigations = {
        "Cybersecurity Threat": (
            "Strengthen identity protection, threat detection, incident response, and customer-facing security guidance."
        ),
        "AI Governance Risk": (
            "Apply responsible AI controls, model evaluation, governance workflows, and human review for high-risk AI use cases."
        ),
        "Regulatory and Compliance Risk": (
            "Coordinate legal, compliance, product, and security teams to monitor regulation and build compliance-by-design controls."
        ),
        "Competitive Pressure": (
            "Track competitor moves, differentiate through product integration, customer value, ecosystem strength, and enterprise trust."
        ),
        "Product Adoption Risk": (
            "Improve onboarding, prove measurable ROI, reduce deployment friction, and prioritize customer success programs."
        ),
        "Cloud and Infrastructure Risk": (
            "Invest in reliability, observability, scalability planning, and transparent service communication."
        ),
        "Reputation and Trust Risk": (
            "Improve transparency, customer communication, public trust signals, and evidence-backed security or privacy commitments."
        ),
        "Partner and Ecosystem Risk": (
            "Reduce dependency risk through partner governance, clear integration standards, and diversified partner support."
        ),
        "General Strategic Risk": (
            "Collect more evidence, assign ownership, and convert the risk into measurable monitoring indicators."
        )
    }

    return mitigations.get(
        category,
        mitigations["General Strategic Risk"]
    )


def create_risk(document):
    score, category = calculate_risk_score(document)

    severity = calculate_severity_level(score)

    confidence = calculate_confidence(
        document=document,
        score=score
    )

    text = document.get("text", "")

    return {
        "risk_title": document.get("title", "Untitled risk"),
        "risk_category": category,
        "severity_level": severity,
        "confidence": confidence,
        "score": score,
        "source": document.get("source", "Unknown source"),
        "source_type": document.get("source_type", "unknown"),
        "published": document.get("published", ""),
        "url": document.get("url", ""),
        "evidence": text[:900],
        "mitigation": build_mitigation(category)
    }


def get_risks(topic="", limit=10):
    documents = get_normalized_documents()

    risks = []

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

        score, _ = calculate_risk_score(document)

        if score <= 0:
            continue

        risk = create_risk(document)
        risks.append(risk)

    risks = sorted(
        risks,
        key=lambda x: (
            x["score"],
            x["confidence"]
        ),
        reverse=True
    )

    return risks[:limit]


def get_risk_summary(topic="", limit=20):
    risks = get_risks(
        topic=topic,
        limit=limit
    )

    severity_counter = Counter(
        risk["severity_level"]
        for risk in risks
    )

    category_counter = Counter(
        risk["risk_category"]
        for risk in risks
    )

    return {
        "risks": risks,
        "severity_counter": severity_counter,
        "category_counter": category_counter,
        "total_risks": len(risks)
    }


if __name__ == "__main__":
    summary = get_risk_summary(
        topic="AI Copilot cloud security",
        limit=10
    )

    print("Total risks:", summary["total_risks"])
    print("Severity levels:", summary["severity_counter"])
    print("Categories:", summary["category_counter"])

    for risk in summary["risks"][:5]:
        print("-" * 80)
        print("Risk:", risk["risk_title"])
        print("Category:", risk["risk_category"])
        print("Severity:", risk["severity_level"])
        print("Confidence:", risk["confidence"])
        print("Source:", risk["source"])