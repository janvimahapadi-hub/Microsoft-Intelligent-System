import os
import json
import pickle
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


DATA_DIR = "data"
FAISS_DIR = "data/faiss_index"

FILES = {
    "raw_documents": "data/raw_documents.json",
    "cleaned_documents": "data/cleaned_documents.json",
    "chunks": "data/chunks.json",
    "embeddings": "data/embeddings.npy",
    "faiss_index": "data/faiss_index/index.faiss",
    "metadata": "data/faiss_index/metadata.pkl",
}


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("\n=== PROJECT DATA AUDIT ===\n")

    for name, path in FILES.items():
        print(f"{name}: {'FOUND' if os.path.exists(path) else 'MISSING'} -> {path}")

    raw_docs = load_json(FILES["raw_documents"])
    cleaned_docs = load_json(FILES["cleaned_documents"])
    chunks = load_json(FILES["chunks"])

    print("\n=== COUNTS ===")
    print("Raw documents:", len(raw_docs) if raw_docs else 0)
    print("Cleaned documents:", len(cleaned_docs) if cleaned_docs else 0)
    print("Chunks:", len(chunks) if chunks else 0)

    if raw_docs:
        sources = set()
        for doc in raw_docs:
            source = doc.get("source") or doc.get("source_name") or doc.get("url") or "unknown"
            sources.add(source)
        print("Estimated unique sources:", len(sources))
        print("Sample sources:", list(sources)[:10])

    if chunks:
        print("\n=== SAMPLE CHUNK ===")
        sample = chunks[0]
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:1500])

        missing_metadata = 0
        for chunk in chunks:
            if not any(k in chunk for k in ["source", "url", "title", "date", "metadata"]):
                missing_metadata += 1

        print("\nChunks missing obvious metadata:", missing_metadata)

    if os.path.exists(FILES["embeddings"]):
        embeddings = np.load(FILES["embeddings"])
        print("\n=== EMBEDDINGS ===")
        print("Embedding shape:", embeddings.shape)

        if chunks:
            print("Chunks match embeddings:", len(chunks) == embeddings.shape[0])

    if faiss and os.path.exists(FILES["faiss_index"]):
        index = faiss.read_index(FILES["faiss_index"])
        print("\n=== FAISS ===")
        print("FAISS vectors:", index.ntotal)

        if chunks:
            print("Chunks match FAISS:", len(chunks) == index.ntotal)

    if os.path.exists(FILES["metadata"]):
        with open(FILES["metadata"], "rb") as f:
            metadata = pickle.load(f)

        print("\n=== METADATA ===")
        print("Metadata records:", len(metadata))
        if metadata:
            print("Sample metadata:")
            print(metadata[0] if isinstance(metadata, list) else list(metadata.items())[:1])


if __name__ == "__main__":
    main()