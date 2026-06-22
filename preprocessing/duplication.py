import json
import hashlib
from pathlib import Path


CLEANED_PATH = Path("data/cleaned_documents.json")


def normalize_for_hash(text):
    return " ".join(text.lower().split())


def create_hash(title, url, content):
    if url:
        base = url.strip().lower()
    else:
        base = normalize_for_hash(title + " " + content[:500])

    return hashlib.md5(base.encode("utf-8")).hexdigest()


def deduplicate_documents():
    if not CLEANED_PATH.exists():
        raise FileNotFoundError(f"Cleaned file not found: {CLEANED_PATH}")

    with open(CLEANED_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file)

    seen = set()
    deduplicated = []

    for doc in documents:
        doc_hash = create_hash(
            title=doc.get("title", ""),
            url=doc.get("url", ""),
            content=doc.get("content", "")
        )

        if doc_hash in seen:
            continue

        seen.add(doc_hash)
        doc["doc_id"] = len(deduplicated)
        deduplicated.append(doc)

    with open(CLEANED_PATH, "w", encoding="utf-8") as file:
        json.dump(deduplicated, file, indent=4, ensure_ascii=False)

    print(f"Before deduplication: {len(documents)}")
    print(f"After deduplication: {len(deduplicated)}")
    print(f"Saved to: {CLEANED_PATH}")


if __name__ == "__main__":
    deduplicate_documents()