import pickle
from pathlib import Path
import utils

import faiss
from sentence_transformers import SentenceTransformer

from utils.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH


class Retriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)

        print("Loading FAISS index...")
        self.index = faiss.read_index(str(FAISS_INDEX_PATH))

        print("Loading metadata...")
        with open(FAISS_METADATA_PATH, "rb") as file:
            self.metadata = pickle.load(file)

        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                f"FAISS index has {self.index.ntotal} vectors, "
                f"but metadata has {len(self.metadata)} records."
            )

        print(f"Retriever ready. Total chunks: {len(self.metadata)}")

    def search(self, query, top_k=5):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        query_embedding = self.model.encode([query]).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []

        for rank, (distance, index_id) in enumerate(
            zip(distances[0], indices[0]),
            start=1
        ):
            if index_id == -1:
                continue

            chunk = self.metadata[index_id]
            evidence_text = chunk.get("chunk_text", "")

            results.append({
                "rank": rank,
                "score": float(distance),
                "chunk_id": chunk.get("chunk_id"),
                "doc_id": chunk.get("doc_id"),
                "title": chunk.get("title", "Unknown title"),
                "source": chunk.get("source", "Unknown source"),
                "source_type": chunk.get("source_type", "unknown"),
                "url": chunk.get("url", ""),
                "published": chunk.get("published", ""),
                "evidence": evidence_text,
                "evidence_length": len(evidence_text)
            })

        return results


if __name__ == "__main__":
    retriever = Retriever()

    test_queries = [
        "What are Microsoft's biggest AI opportunities?",
        "What are Microsoft's biggest risks in cloud and AI?",
        "What are competitors doing against Microsoft?",
        "What emerging technology trends should Microsoft monitor?",
        "If you were Microsoft's CEO today, what strategic action would you prioritize?"
    ]

    for query in test_queries:
        print("\n" + "=" * 120)
        print("QUERY:", query)
        print("=" * 120)

        results = retriever.search(query, top_k=5)

        for result in results:
            print("\n" + "-" * 100)
            print(f"Result {result['rank']}")
            print("Chunk ID:", result["chunk_id"])
            print("Document ID:", result["doc_id"])
            print("Title:", result["title"])
            print("Source:", result["source"])
            print("Source Type:", result["source_type"])
            print("Published:", result["published"])
            print("Score:", result["score"])
            print("URL:", result["url"])
            print("Evidence Length:", result["evidence_length"])
            print("\nEvidence Preview:")
            print(result["evidence"][:700])