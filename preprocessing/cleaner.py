import json
import re
from pathlib import Path


RAW_PATH = Path("data/raw_documents.json")
CLEANED_PATH = Path("data/cleaned_documents.json")


BAD_TERMS = [
    "weekly employment",
    "employment q&a",
    "job search",
    "resume",
    "interview",
    "hiring",
    "study buddy",
    "open to work"
]


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_bad_document(title, content):
    combined = f"{title} {content}".lower()
    return any(term in combined for term in BAD_TERMS)


def clean_documents():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    with open(RAW_PATH, "r", encoding="utf-8") as file:
        raw_documents = json.load(file)

    cleaned_documents = []

    for idx, doc in enumerate(raw_documents):
        title = clean_text(doc.get("title", ""))
        content = clean_text(doc.get("content", ""))

        if not title or not content:
            continue

        if len(content) < 100:
            continue

        if is_bad_document(title, content):
            continue

        cleaned_documents.append({
            "doc_id": len(cleaned_documents),
            "title": title,
            "source": doc.get("source", "Unknown source"),
            "source_type": doc.get("source_type", "unknown"),
            "company": doc.get("company", doc.get("competitor", "Microsoft")),
            "competitor": doc.get("competitor", ""),
            "url": doc.get("url", ""),
            "published": doc.get("published", ""),
            "content": content,
            "summary": clean_text(doc.get("summary", "")),
            "content_length": len(content)
        })

    CLEANED_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CLEANED_PATH, "w", encoding="utf-8") as file:
        json.dump(cleaned_documents, file, indent=4, ensure_ascii=False)

    print(f"Raw documents: {len(raw_documents)}")
    print(f"Cleaned documents: {len(cleaned_documents)}")
    print(f"Saved to: {CLEANED_PATH}")


if __name__ == "__main__":
    clean_documents()