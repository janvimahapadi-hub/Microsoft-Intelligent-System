import json
import os
import pickle
from collections import Counter
from datetime import datetime

from utils.config import (
    RAW_DOCS_PATH,
    CLEANED_DOCS_PATH,
    CHUNKS_PATH,
    FAISS_METADATA_PATH
)


def load_json_file(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_pickle_file(path):
    if not os.path.exists(path):
        return []

    with open(path, "rb") as file:
        return pickle.load(file)


def get_raw_documents():
    return load_json_file(RAW_DOCS_PATH)


def get_cleaned_documents():
    return load_json_file(CLEANED_DOCS_PATH)


def get_chunks():
    return load_json_file(CHUNKS_PATH)


def get_faiss_metadata():
    return load_pickle_file(FAISS_METADATA_PATH)


def get_document_text(document):
    return (
        document.get("content")
        or document.get("text")
        or document.get("chunk_text")
        or document.get("description")
        or ""
    )


def get_document_source(document):
    return (
        document.get("source")
        or document.get("source_name")
        or document.get("source_type")
        or "Unknown source"
    )


def get_document_title(document):
    return (
        document.get("title")
        or document.get("headline")
        or "Untitled document"
    )


def get_document_url(document):
    return document.get("url") or ""


def get_document_date(document):
    return (
        document.get("published")
        or document.get("date")
        or document.get("created_at")
        or document.get("timestamp")
        or ""
    )


def get_source_statistics(documents):
    sources = [
        get_document_source(doc)
        for doc in documents
    ]

    return Counter(sources)


def get_source_type_statistics(documents):
    source_types = [
        doc.get("source_type", "unknown")
        for doc in documents
    ]

    return Counter(source_types)


def get_latest_update_timestamp(documents):
    dates = []

    for doc in documents:
        date_value = get_document_date(doc)
        if date_value:
            dates.append(date_value)

    if not dates:
        return "Unknown"

    return sorted(dates)[-1]


def get_project_overview():
    raw_documents = get_raw_documents()
    cleaned_documents = get_cleaned_documents()
    chunks = get_chunks()
    metadata = get_faiss_metadata()

    source_stats = get_source_statistics(raw_documents)
    source_type_stats = get_source_type_statistics(raw_documents)

    overview = {
        "company_name": "Microsoft",
        "industry": "Technology, Cloud, AI, Software",
        "raw_documents": len(raw_documents),
        "cleaned_documents": len(cleaned_documents),
        "chunks": len(chunks),
        "indexed_vectors": len(metadata),
        "unique_sources": len(source_stats),
        "source_stats": source_stats,
        "source_type_stats": source_type_stats,
        "last_update": get_latest_update_timestamp(raw_documents),
        "dashboard_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return overview


def get_recent_documents(limit=10):
    documents = get_raw_documents()

    def sort_key(doc):
        return get_document_date(doc)

    documents = sorted(
        documents,
        key=sort_key,
        reverse=True
    )

    return documents[:limit]

def normalize_document(document):
    """
    Converts different document structures into one consistent format.
    This helps dashboard pages work even when collectors store fields differently.
    """

    return {
        "title": get_document_title(document),
        "source": get_document_source(document),
        "source_type": document.get("source_type", "unknown"),
        "url": get_document_url(document),
        "published": get_document_date(document),
        "text": get_document_text(document),
        "raw": document
    }


def get_normalized_documents():
    documents = get_raw_documents()

    return [
        normalize_document(doc)
        for doc in documents
    ]