import json


CLEANED_PATH = "data/cleaned_documents.json"
CHUNKS_PATH = "data/chunks.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def create_chunks(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - CHUNK_OVERLAP

    return chunks


def chunk_documents(documents):
    all_chunks = []
    chunk_id = 1

    for doc in documents:
        full_text = f"{doc.get('title', '')}. {doc.get('content', '')}"
        chunks = create_chunks(full_text)

        for chunk_text in chunks:
            all_chunks.append({
                "chunk_id": chunk_id,
                "doc_id": doc.get("doc_id"),
                "title": doc.get("title"),
                "source": doc.get("source"),
                "source_type": doc.get("source_type"),
                "url": doc.get("url"),
                "published": doc.get("published"),
                "chunk_text": chunk_text
            })
            chunk_id += 1

    return all_chunks


def main():
    with open(CLEANED_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file)

    chunks = chunk_documents(documents)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)

    print(f"Cleaned documents: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Saved to: {CHUNKS_PATH}")


if __name__ == "__main__":
    main()