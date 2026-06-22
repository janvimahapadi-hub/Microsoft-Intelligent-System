import json
from pathlib import Path


CLEANED_PATH = Path("data/cleaned_documents.json")
CHUNKS_PATH = Path("data/chunks.json")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def load_cleaned_documents():
    if not CLEANED_PATH.exists():
        raise FileNotFoundError(f"Cleaned documents file not found: {CLEANED_PATH}")

    with open(CLEANED_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not documents:
        raise ValueError("cleaned_documents.json is empty. Run cleaner.py first.")

    return documents


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(chunk_text)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= text_length:
            break

    return chunks


def create_chunks():
    documents = load_cleaned_documents()
    chunks = []
    chunk_id = 0

    for doc in documents:
        content = doc.get("content", "")

        text_chunks = split_text(content)

        for chunk_text in text_chunks:
            chunk = {
                "chunk_id": chunk_id,
                "doc_id": doc.get("doc_id"),
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "source_type": doc.get("source_type", ""),
                "company": doc.get("company", ""),
                "competitor": doc.get("competitor", ""),
                "url": doc.get("url", ""),
                "published": doc.get("published", ""),
                "chunk_text": chunk_text
            }

            chunks.append(chunk)
            chunk_id += 1

    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Saved to: {CHUNKS_PATH}")


if __name__ == "__main__":
    create_chunks()