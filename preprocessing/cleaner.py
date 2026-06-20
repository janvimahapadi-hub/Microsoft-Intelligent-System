import json
import re
from bs4 import BeautifulSoup


RAW_PATH = "data/raw_documents.json"
CLEANED_PATH = "data/cleaned_documents.json"


def clean_text(text):
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(" ", strip=True)

    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_documents(raw_documents):
    cleaned_documents = []

    for i, doc in enumerate(raw_documents):
        title = clean_text(doc.get("title", ""))
        content = clean_text(doc.get("content", ""))

        if not title and not content:
            continue

        cleaned_documents.append({
            "doc_id": i + 1,
            "title": title,
            "source": doc.get("source", ""),
            "source_type": doc.get("source_type", ""),
            "url": doc.get("url", ""),
            "published": doc.get("published", ""),
            "content": content,
            "content_length": len(content),
            "used_full_article": doc.get("used_full_article", False),
            "collected_at": doc.get("collected_at", "")
        })

    return cleaned_documents


def main():
    with open(RAW_PATH, "r", encoding="utf-8") as file:
        raw_documents = json.load(file)

    cleaned_documents = clean_documents(raw_documents)

    with open(CLEANED_PATH, "w", encoding="utf-8") as file:
        json.dump(cleaned_documents, file, indent=4, ensure_ascii=False)

    print(f"Raw documents: {len(raw_documents)}")
    print(f"Cleaned documents: {len(cleaned_documents)}")
    print(f"Saved to: {CLEANED_PATH}")


if __name__ == "__main__":
    main()