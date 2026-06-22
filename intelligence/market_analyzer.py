from collections import Counter

from utils.data_loader import get_normalized_documents


EMERGING_TECH_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "copilot",
    "agent",
    "agents",
    "azure ai",
    "foundry",
    "cloud",
    "security",
    "defender",
    "entra",
    "github",
    "developer",
    "model",
    "automation",
    "data",
    "quantum",
    "windows",
    "microsoft 365"
]


COMPETITOR_KEYWORDS = [
    "aws",
    "amazon",
    "google",
    "google cloud",
    "nvidia",
    "apple",
    "meta",
    "openai",
    "anthropic",
    "oracle",
    "salesforce",
    "sap",
    "adobe",
    "ibm"
]


ANNOUNCEMENT_KEYWORDS = [
    "announced",
    "introduces",
    "introduced",
    "launch",
    "launched",
    "available",
    "general availability",
    "preview",
    "new",
    "update",
    "build",
    "ignite",
    "release"
]


RISK_KEYWORDS = [
    "risk",
    "threat",
    "attack",
    "cyberattack",
    "security",
    "vulnerability",
    "regulation",
    "compliance",
    "privacy",
    "competition",
    "challenge",
    "concern",
    "incident"
]


OPPORTUNITY_KEYWORDS = [
    "opportunity",
    "growth",
    "partner",
    "customers",
    "adoption",
    "productivity",
    "transformation",
    "enterprise",
    "revenue",
    "innovation",
    "scale",
    "platform"
]


def contains_any(text, keywords):
    text = text.lower()

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def keyword_score(text, keywords):
    text = text.lower()

    score = 0

    for keyword in keywords:
        if keyword.lower() in text:
            score += 1

    return score


def combined_text(document):
    return f"{document.get('title', '')} {document.get('text', '')}".lower()


def is_relevant_to_topic(document, topic):
    if not topic or not topic.strip():
        return True

    topic_words = [
        word.strip().lower()
        for word in topic.replace(",", " ").split()
        if len(word.strip()) > 2
    ]

    text = combined_text(document)

    return any(word in text for word in topic_words)


def classify_market_signal(document):
    text = combined_text(document)

    signal_types = []

    if document.get("source_type") == "official":
        signal_types.append("Company Announcement")

    if contains_any(text, ANNOUNCEMENT_KEYWORDS):
        signal_types.append("Company Announcement")

    if contains_any(text, COMPETITOR_KEYWORDS):
        signal_types.append("Competitor Activity")

    if contains_any(text, EMERGING_TECH_KEYWORDS):
        signal_types.append("Emerging Technology")

    if contains_any(text, RISK_KEYWORDS):
        signal_types.append("Risk Signal")

    if contains_any(text, OPPORTUNITY_KEYWORDS):
        signal_types.append("Opportunity Signal")

    if not signal_types:
        signal_types.append("General Market Signal")

    return signal_types


def rank_documents(documents, topic="", limit=20):
    ranked = []

    for document in documents:
        if not is_relevant_to_topic(document, topic):
            continue

        text = combined_text(document)

        score = 0
        score += keyword_score(text, EMERGING_TECH_KEYWORDS) * 2
        score += keyword_score(text, OPPORTUNITY_KEYWORDS) * 2
        score += keyword_score(text, RISK_KEYWORDS) * 2
        score += keyword_score(text, COMPETITOR_KEYWORDS) * 3
        score += keyword_score(text, ANNOUNCEMENT_KEYWORDS)

        if topic:
            topic_words = [
                word.strip().lower()
                for word in topic.replace(",", " ").split()
                if len(word.strip()) > 2
            ]

            for word in topic_words:
                if word in text:
                    score += 3

        ranked.append({
            **document,
            "market_score": score,
            "signal_types": classify_market_signal(document)
        })

    ranked = sorted(
        ranked,
        key=lambda x: (
            x.get("market_score", 0),
            x.get("published", "")
        ),
        reverse=True
    )

    return ranked[:limit]


def get_market_intelligence(topic="", limit=20):
    documents = get_normalized_documents()

    ranked_documents = rank_documents(
        documents=documents,
        topic=topic,
        limit=limit
    )

    signal_counter = Counter()

    source_counter = Counter()

    for document in ranked_documents:
        for signal in document.get("signal_types", []):
            signal_counter[signal] += 1

        source_counter[document.get("source", "Unknown source")] += 1

    market_intelligence = {
        "topic": topic,
        "documents": ranked_documents,
        "signal_counter": signal_counter,
        "source_counter": source_counter,
        "total_results": len(ranked_documents)
    }

    return market_intelligence


def get_documents_by_signal(signal_name, topic="", limit=10):
    market_data = get_market_intelligence(
        topic=topic,
        limit=50
    )

    results = []

    for document in market_data["documents"]:
        if signal_name in document.get("signal_types", []):
            results.append(document)

    return results[:limit]


if __name__ == "__main__":
    data = get_market_intelligence(
        topic="AI Copilot cloud security",
        limit=10
    )

    print("Total results:", data["total_results"])
    print("Signals:", data["signal_counter"])

    for doc in data["documents"][:5]:
        print("-" * 80)
        print(doc["title"])
        print(doc["source"])
        print(doc["signal_types"])
        print(doc["url"])