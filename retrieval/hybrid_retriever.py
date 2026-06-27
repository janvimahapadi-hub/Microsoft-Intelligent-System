import pickle
import re

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from utils.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH


BAD_TERMS = [
    "weekly employment",
    "employment q&a",
    "job search",
    "resume",
    "interview",
    "hiring",
    "study buddy",
    "open to work",
]


COMPETITORS = [
    "aws",
    "google",
    "google cloud",
    "openai",
    "anthropic",
    "nvidia",
]


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()


def is_bad_result(item):
    title = item.get("title", "").lower()
    evidence = item.get("evidence", "").lower()
    source = item.get("source", "").lower()

    if any(term in title or term in evidence for term in BAD_TERMS):
        return True

    if "reddit" in source and any(term in title for term in BAD_TERMS):
        return True

    return False


def competitor_bonus(item):
    company = item.get("company", "").lower()
    source = item.get("source", "").lower()

    if any(comp in company or comp in source for comp in COMPETITORS):
        return 0.10

    return 0.0


class HybridRetriever:
    """
    Hybrid retrieval = FAISS semantic search + BM25 keyword search.

    FAISS finds meaning-based matches.
    BM25 finds exact keyword matches.
    Source diversity prevents repeated chunks from the same article.
    Competitor bonus improves retrieval diversity for competitive strategy questions.
    """

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

        print("Preparing BM25 corpus...")
        self.texts = []

        for item in self.metadata:
            combined_text = " ".join([
                item.get("title", ""),
                item.get("source", ""),
                item.get("company", ""),
                item.get("competitor", ""),
                item.get("chunk_text", "")
            ])
            self.texts.append(combined_text)

        tokenized_corpus = [tokenize(text) for text in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

        print(f"Hybrid retriever ready. Total chunks: {len(self.metadata)}")

    def search(self, query, top_k=5):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        candidate_k = min(max(top_k * 12, 40), len(self.metadata))

        # -----------------------------
        # FAISS semantic retrieval
        # -----------------------------
        query_embedding = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_embedding, candidate_k)

        faiss_scores = {}

        for distance, index_id in zip(distances[0], indices[0]):
            if index_id == -1:
                continue

            faiss_scores[int(index_id)] = float(distance)

        # Normalize FAISS L2 distance into similarity score.
        # Lower distance = better, so invert it.
        normalized_faiss = {}

        if faiss_scores:
            max_distance = max(faiss_scores.values())
            min_distance = min(faiss_scores.values())

            for idx, dist in faiss_scores.items():
                if max_distance == min_distance:
                    normalized_faiss[idx] = 1.0
                else:
                    normalized_faiss[idx] = 1 - (
                        (dist - min_distance) / (max_distance - min_distance)
                    )

        
        # BM25 keyword retrieval
    
        tokenized_query = tokenize(query)
        bm25_scores_raw = self.bm25.get_scores(tokenized_query)

        top_bm25_indices = np.argsort(bm25_scores_raw)[::-1][:candidate_k]

        bm25_scores = {
            int(idx): float(bm25_scores_raw[idx])
            for idx in top_bm25_indices
        }

        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0

        normalized_bm25 = {}

        for idx, score in bm25_scores.items():
            if max_bm25 == 0:
                normalized_bm25[idx] = 0.0
            else:
                normalized_bm25[idx] = score / max_bm25

        # -----------------------------
        # Combine scores
        # -----------------------------
        all_candidate_ids = set(normalized_faiss.keys()) | set(normalized_bm25.keys())

        results = []

        for index_id in all_candidate_ids:
            chunk = self.metadata[index_id]
            evidence_text = chunk.get("chunk_text", "")

            item = {
                "chunk_id": chunk.get("chunk_id"),
                "doc_id": chunk.get("doc_id"),
                "title": chunk.get("title", "Unknown title"),
                "source": chunk.get("source", "Unknown source"),
                "source_type": chunk.get("source_type", "unknown"),
                "company": chunk.get("company", ""),
                "competitor": chunk.get("competitor", ""),
                "url": chunk.get("url", ""),
                "published": chunk.get("published", ""),
                "evidence": evidence_text,
                "evidence_length": len(evidence_text),
                "faiss_score": round(normalized_faiss.get(index_id, 0.0), 4),
                "bm25_score": round(normalized_bm25.get(index_id, 0.0), 4),
            }

            if is_bad_result(item):
                continue

            item["competitor_bonus"] = competitor_bonus(item)

            item["hybrid_score"] = round(
                (0.65 * item["faiss_score"])
                + (0.35 * item["bm25_score"])
                + item["competitor_bonus"],
                4
            )

            # Compatibility with older code:
            # Older retriever used lower score = better.
            item["score"] = round(1 - item["hybrid_score"], 4)

            results.append(item)

        results = sorted(
            results,
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # -----------------------------
        # Source diversity filter
        # Avoid returning multiple chunks from same URL/article.
        # -----------------------------
        diverse_results = []
        seen_urls = set()
        seen_titles = set()

        for item in results:
            url = item.get("url", "")
            title = item.get("title", "").lower().strip()

            if url and url in seen_urls:
                continue

            if title and title in seen_titles:
                continue

            if url:
                seen_urls.add(url)

            if title:
                seen_titles.add(title)

            diverse_results.append(item)

            if len(diverse_results) >= top_k:
                break

        for rank, item in enumerate(diverse_results, start=1):
            item["rank"] = rank

        return diverse_results


if __name__ == "__main__":
    retriever = HybridRetriever()

    test_queries = [
        "What are Microsoft's biggest AI opportunities?",
        "What are Microsoft's biggest cybersecurity risks?",
        "How should Microsoft strengthen Azure against AWS and Google Cloud?",
        "What is Microsoft doing with AI agents and Foundry?",
        "How should Microsoft compete with AWS and Google Cloud in AI infrastructure?",
        "What competitive threats does OpenAI pose to Microsoft?",
    ]

    for query in test_queries:
        print("\n" + "=" * 100)
        print("QUERY:", query)
        print("=" * 100)

        results = retriever.search(query, top_k=5)

        for result in results:
            print("\n" + "-" * 80)
            print("Rank:", result["rank"])
            print("Title:", result["title"])
            print("Source:", result["source"])
            print("Company:", result.get("company", ""))
            print("Hybrid Score:", result["hybrid_score"])
            print("FAISS Score:", result["faiss_score"])
            print("BM25 Score:", result["bm25_score"])
            print("Competitor Bonus:", result["competitor_bonus"])
            print("URL:", result["url"])
            print("Preview:")
            print(result["evidence"][:400])