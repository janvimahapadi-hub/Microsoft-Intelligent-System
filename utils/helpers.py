import json
from datetime import datetime


# ==========================================================
# JSON HELPERS
# ==========================================================

def load_json(path):
    """
    Load JSON file safely.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    """
    Save JSON file safely.
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ==========================================================
# TEXT HELPERS
# ==========================================================

def truncate_text(text, max_length=500):
    """
    Shortens long evidence previews.
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def normalize_whitespace(text):
    """
    Remove extra spaces/newlines.
    """
    if not text:
        return ""

    return " ".join(text.split())


# ==========================================================
# EVIDENCE HELPERS
# ==========================================================

def format_evidence(item):
    """
    Standard evidence formatting.
    """

    return {
        "title": item.get("title", "Unknown"),
        "source": item.get("source", "Unknown"),
        "source_type": item.get("source_type", "Unknown"),
        "published": item.get("published", ""),
        "url": item.get("url", ""),
        "evidence": item.get("evidence", "")
    }


# ==========================================================
# SOURCE FILTERING
# ==========================================================

BAD_TERMS = [
    "weekly employment",
    "employment q&a",
    "resume",
    "interview",
    "hiring",
    "job search",
    "open to work",
    "study buddy"
]


def is_low_value_source(item):
    """
    Remove low-value strategic intelligence documents.
    """

    title = item.get("title", "").lower()
    evidence = item.get("evidence", "").lower()

    for term in BAD_TERMS:
        if term in title or term in evidence:
            return True

    return False


# ==========================================================
# CONFIDENCE SCORING
# ==========================================================

def calculate_confidence(evidence_items):
    """
    Simple confidence score.

    More evidence diversity = higher confidence.
    """

    if not evidence_items:
        return 0.0

    unique_sources = len(
        set(
            item.get("source", "")
            for item in evidence_items
        )
    )

    evidence_count = len(evidence_items)

    confidence = (
        (evidence_count * 0.15)
        +
        (unique_sources * 0.20)
    )

    return round(min(confidence, 1.0), 2)


# ==========================================================
# DATE HELPERS
# ==========================================================

def format_date(date_string):
    """
    Converts RSS dates to cleaner format.
    """

    if not date_string:
        return "Unknown"

    try:
        dt = datetime.strptime(
            date_string[:25],
            "%a, %d %b %Y %H:%M:%S"
        )

        return dt.strftime("%d %b %Y")

    except Exception:
        return date_string


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def build_executive_summary(
    opportunities,
    risks,
    top_topic
):
    """
    Small reusable executive summary.
    """

    return f"""
The intelligence base contains
{opportunities} opportunity signals
and {risks} risk signals.

The dominant strategic topic is
'{top_topic}'.

Management should prioritize
high-value opportunities while
actively monitoring emerging risks.
"""