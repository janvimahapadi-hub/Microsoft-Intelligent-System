import json
from pathlib import Path
from transformers import pipeline


INPUT_PATH = Path("data/cleaned_documents.json")
OUTPUT_PATH = Path("data/sentiment_results.json")


TOPIC_KEYWORDS = {
    "AI Opportunity": ["copilot", "foundry", "agent", "ai", "model", "automation"],
    "Cloud Strategy": ["azure", "cloud", "infrastructure", "datacenter"],
    "Security Risk": ["security", "defender", "threat", "risk", "attack", "governance"],
    "Partnership": ["partner", "ecosystem", "collaboration"],
    "Developer Productivity": ["github", "developer", "code", "build"],
    "Market / Community": ["reddit", "community", "customer", "feedback"]
}


def classify_topic(text):
    text = text.lower()

    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for word in keywords if word in text)

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return "General Strategy"

    return best_topic


def normalize_sentiment(label, score):
    if label.upper() == "POSITIVE":
        return "Positive", round(score, 3)

    if label.upper() == "NEGATIVE":
        return "Negative", round(score, 3)

    return "Neutral", round(score, 3)


def analyze_sentiment():
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file)

    print(f"Loaded documents: {len(documents)}")

    sentiment_model = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    results = []

    for doc in documents:
        title = doc.get("title", "")
        content = doc.get("content", "")

        text_for_analysis = f"{title}. {content[:800]}"

        prediction = sentiment_model(text_for_analysis[:512])[0]

        sentiment_label, sentiment_score = normalize_sentiment(
            prediction["label"],
            prediction["score"]
        )

        topic = classify_topic(text_for_analysis)

        results.append({
            "doc_id": doc.get("doc_id"),
            "title": title,
            "source": doc.get("source", ""),
            "source_type": doc.get("source_type", ""),
            "url": doc.get("url", ""),
            "published": doc.get("published", ""),
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "topic": topic,
            "preview": content[:300]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print(f"Sentiment results saved to: {OUTPUT_PATH}")
    print(f"Total analyzed: {len(results)}")


if __name__ == "__main__":
    analyze_sentiment()