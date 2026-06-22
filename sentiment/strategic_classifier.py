import json
from pathlib import Path


INPUT_PATH = Path("data/sentiment_results.json")
OUTPUT_PATH = Path("data/sentiment_results.json")


RISK_KEYWORDS = [
    "risk", "security", "threat", "attack", "breach", "vulnerability",
    "compliance", "regulation", "governance", "privacy", "trust",
    "cost", "competition", "concern", "challenge", "issue", "failure"
]

OPPORTUNITY_KEYWORDS = [
    "growth", "adoption", "launch", "innovation", "copilot", "agent",
    "foundry", "azure", "productivity", "partnership", "enterprise",
    "developer", "platform", "automation", "customer", "scale"
]

IRRELEVANT_KEYWORDS = [
    "study buddy", "open to work", "job search", "resume",
    "interview", "hiring", "employment q&a", "weekly employment"
]


def classify_strategic_signal(text):
    text = text.lower()

    if any(word in text for word in IRRELEVANT_KEYWORDS):
        return "Irrelevant"

    risk_score = sum(1 for word in RISK_KEYWORDS if word in text)
    opportunity_score = sum(1 for word in OPPORTUNITY_KEYWORDS if word in text)

    if risk_score > opportunity_score:
        return "Risk"

    if opportunity_score > risk_score:
        return "Opportunity"

    return "Neutral"


def classify_strength(text):
    text = text.lower()

    keyword_count = 0

    for word in RISK_KEYWORDS + OPPORTUNITY_KEYWORDS:
        if word in text:
            keyword_count += 1

    if keyword_count >= 6:
        return "High"

    if keyword_count >= 3:
        return "Medium"

    return "Low"


def update_sentiment_results():
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        results = json.load(file)

    updated_results = []

    for item in results:
        combined_text = " ".join([
            item.get("title", ""),
            item.get("topic", ""),
            item.get("preview", ""),
            item.get("source", "")
        ])

        strategic_signal = classify_strategic_signal(combined_text)
        signal_strength = classify_strength(combined_text)

        item["strategic_signal"] = strategic_signal
        item["signal_strength"] = signal_strength

        updated_results.append(item)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(updated_results, file, indent=4, ensure_ascii=False)

    print("Strategic classification completed.")
    print(f"Total documents updated: {len(updated_results)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    update_sentiment_results()