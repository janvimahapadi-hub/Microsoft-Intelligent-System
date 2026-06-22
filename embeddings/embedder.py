import json
import numpy as np
from sentence_transformers import SentenceTransformer


CHUNKS_PATH = "data/chunks.json"
EMBEDDINGS_PATH = "data/embeddings.npy"


def generate_embeddings():

    print("Loading chunks...")

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    texts = [
        chunk["chunk_text"]
        for chunk in chunks
    ]

    print("Loading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    np.save(
        EMBEDDINGS_PATH,
        embeddings
    )

    print(
        f"Embeddings shape: {embeddings.shape}"
    )

    print(
        f"Saved to: {EMBEDDINGS_PATH}"
    )


if __name__ == "__main__":
    generate_embeddings()