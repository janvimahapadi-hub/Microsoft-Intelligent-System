from collections import Counter, defaultdict
from datetime import datetime

import pandas as pd

from utils.data_loader import get_normalized_documents


POSITIVE_WORDS = [
    "growth",
    "opportunity",
    "improve",
    "improved",
    "innovation",
    "innovative",
    "secure",
    "trusted",
    "trust",
    "success",
    "successful",
    "accelerate",
    "accelerating",
    "enable",
    "enabling",
    "productivity",
    "efficient",
    "efficiency",
    "scale",
    "scalable",
    "adoption",
    "strong",
    "leader",
    "leading",
    "benefit",
    "benefits",
    "performance",
    "reliable",
    "available",
    "launch",
    "launched",
    "expand",
    "expanded",
    "partnership",
    "partners",
    "customer",
    "customers",
    "value"
]


NEGATIVE_WORDS = [
    "risk",
    "threat",
    "attack",
    "cyberattack",
    "breach",
    "vulnerability",
    "concern",
    "concerns",
    "problem",
    "issue",
    "issues",
    "failure",
    "failed",
    "delay",
    "delayed",
    "outage",
    "competition",
    "competitive",
    "pressure",
    "privacy",
    "regulation",
    "regulatory",
    "compliance",
    "cost",
    "expensive",
    "challenge",
    "challenging",
    "criticism",
    "criticized",
    "slow",
    "weak",
    "uncertainty",
    "riskier",
    "malware",
    "phishing",
    "ransomware"
]


def combined_text(document):
    return f"{document.get('title', '')} {document.get('text', '')}".lower()


def count_keywords(text, keywords):
    text = text.lower()

    count = 0

    for keyword in keywords:
        if keyword.lower() in text:
            count += 1

    return count


def calculate_sentiment_score(document):
    text = combined_text(document)

    positive_count = count_keywords(text, POSITIVE_WORDS)
    negative_count = count_keywords(text, NEGATIVE_WORDS)

    total = positive_count + negative_count

    if total == 0:
        score = 0.0
    else:
        score = (positive_count - negative_count) / total

    if score > 0.15:
        label = "Positive"
    elif score < -0.15:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "sentiment_score": round(score, 3),
        "sentiment_label": label,
        "positive_terms": positive_count,
        "negative_terms": negative_count
    }


def is_public_or_community_source(document):
    source = document.get("source", "").lower()
    source_type = document.get("source_type", "").lower()
    url = document.get("url", "").lower()

    public_markers = [
        "reddit",
        "community",
        "forum",
        "social",
        "public"
    ]

    text = f"{source} {source_type} {url}"

    return any(marker in text for marker in public_markers)


def is_news_or_external_source(document):
    source = document.get("source", "").lower()
    source_type = document.get("source_type", "").lower()

    markers = [
        "news",
        "external",
        "reddit",
        "community"
    ]

    text = f"{source} {source_type}"

    return any(marker in text for marker in markers)


def is_official_source(document):
    source_type = document.get("source_type", "").lower()
    source = document.get("source", "").lower()

    return source_type == "official" or "microsoft" in source


def parse_date(date_value):
    if not date_value:
        return None

    try:
        return pd.to_datetime(date_value, errors="coerce", utc=True).date()
    except Exception:
        return None


def document_matches_topic(document, topic):
    if not topic or not topic.strip():
        return True

    text = combined_text(document)

    topic_words = [
        word.strip().lower()
        for word in topic.replace(",", " ").split()
        if len(word.strip()) > 2
    ]

    return any(word in text for word in topic_words)


def analyze_document_sentiment(document):
    sentiment = calculate_sentiment_score(document)

    source_group = "Other"

    if is_public_or_community_source(document):
        source_group = "Public / Community"
    elif is_news_or_external_source(document):
        source_group = "News / External"
    elif is_official_source(document):
        source_group = "Official"

    parsed_date = parse_date(document.get("published", ""))

    return {
        "title": document.get("title", "Untitled document"),
        "source": document.get("source", "Unknown source"),
        "source_type": document.get("source_type", "unknown"),
        "source_group": source_group,
        "published": document.get("published", ""),
        "parsed_date": parsed_date,
        "url": document.get("url", ""),
        "text": document.get("text", ""),
        "sentiment_score": sentiment["sentiment_score"],
        "sentiment_label": sentiment["sentiment_label"],
        "positive_terms": sentiment["positive_terms"],
        "negative_terms": sentiment["negative_terms"]
    }


def get_sentiment_analysis(topic="", limit=100):
    documents = get_normalized_documents()

    analyzed = []

    for document in documents:
        if not document_matches_topic(document, topic):
            continue

        analyzed.append(
            analyze_document_sentiment(document)
        )

    analyzed = sorted(
        analyzed,
        key=lambda x: abs(x["sentiment_score"]),
        reverse=True
    )

    analyzed = analyzed[:limit]

    label_counter = Counter(
        item["sentiment_label"]
        for item in analyzed
    )

    source_group_counter = Counter(
        item["source_group"]
        for item in analyzed
    )

    source_sentiment = defaultdict(list)

    for item in analyzed:
        source_sentiment[item["source_group"]].append(
            item["sentiment_score"]
        )

    average_by_source_group = {}

    for group, scores in source_sentiment.items():
        if scores:
            average_by_source_group[group] = round(
                sum(scores) / len(scores),
                3
            )

    overall_average = 0.0

    if analyzed:
        overall_average = round(
            sum(item["sentiment_score"] for item in analyzed) / len(analyzed),
            3
        )

    return {
        "topic": topic,
        "documents": analyzed,
        "label_counter": label_counter,
        "source_group_counter": source_group_counter,
        "average_by_source_group": average_by_source_group,
        "overall_average": overall_average,
        "total_documents": len(analyzed)
    }


def get_sentiment_trend(topic="", limit=100):
    sentiment_data = get_sentiment_analysis(
        topic=topic,
        limit=limit
    )

    trend = defaultdict(list)

    for item in sentiment_data["documents"]:
        parsed_date = item.get("parsed_date")

        if parsed_date is None:
            continue

        trend[parsed_date].append(
            item["sentiment_score"]
        )

    rows = []

    for date_value, scores in trend.items():
        rows.append({
            "Date": date_value,
            "Average Sentiment": round(sum(scores) / len(scores), 3),
            "Document Count": len(scores)
        })

    rows = sorted(
        rows,
        key=lambda x: x["Date"]
    )

    return rows


if __name__ == "__main__":
    result = get_sentiment_analysis(
        topic="AI Copilot security",
        limit=20
    )

    print("Total documents:", result["total_documents"])
    print("Overall average:", result["overall_average"])
    print("Labels:", result["label_counter"])
    print("Source groups:", result["source_group_counter"])
    print("Average by source group:", result["average_by_source_group"])

    for item in result["documents"][:5]:
        print("-" * 80)
        print(item["title"])
        print(item["source_group"])
        print(item["sentiment_label"], item["sentiment_score"])