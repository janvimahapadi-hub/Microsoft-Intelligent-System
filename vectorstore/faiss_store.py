import json
import os
import pickle

import faiss
import numpy as np


CHUNKS_PATH = "data/chunks.json"
EMBEDDINGS_PATH = "data/embeddings.npy"
FAISS_INDEX_PATH = "data/faiss_index/index.faiss"
METADATA_PATH = "data/faiss_index/metadata.pkl"


def build_faiss_index():
    os.makedirs("data/faiss_index", exist_ok=True)

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)             ##IndexFlatIP=used for semantic similarity
    index.add(embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(METADATA_PATH, "wb") as file:
        pickle.dump(chunks, file)

    print(f"Chunks loaded: {len(chunks)}")
    print(f"Embeddings loaded: {embeddings.shape}")
    print(f"FAISS vectors stored: {index.ntotal}")
    print(f"FAISS index saved to: {FAISS_INDEX_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    build_faiss_index()