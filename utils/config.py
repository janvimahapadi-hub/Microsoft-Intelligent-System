from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DOCS_PATH = DATA_DIR / "raw_documents.json"
CLEANED_DOCS_PATH = DATA_DIR / "cleaned_documents.json"
CHUNKS_PATH = DATA_DIR / "chunks.json"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"

FAISS_DIR = DATA_DIR / "faiss_index"
FAISS_INDEX_PATH = FAISS_DIR / "index.faiss"
FAISS_METADATA_PATH = FAISS_DIR / "metadata.pkl"