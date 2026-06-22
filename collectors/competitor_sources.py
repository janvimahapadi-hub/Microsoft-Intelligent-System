import json
import re
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup


RAW_DOCUMENTS_PATH = Path("data/raw_documents.json")

MAX_ITEMS_PER_FEED = 8
REQUEST_TIMEOUT = 15


COMPETITOR_FEEDS = [
    {
        "company": "Google",
        "source": "Google Blog",
        "source_type": "competitor",
        "feed_url": "https://blog.google/feed/",
    },
    {
        "company": "Google Cloud",
        "source": "Google Cloud Blog",
        "source_type": "competitor",
        "feed_url": "https://cloudblog.withgoogle.com/rss/",
    },
    {
        "company": "AWS",
        "source": "AWS Blog",
        "source_type": "competitor",
        "feed_url": "https://aws.amazon.com/blogs/aws/feed/",
    },
    {
        "company": "AWS",
        "source": "AWS Machine Learning Blog",
        "source_type": "competitor",
        "feed_url": "https://aws.amazon.com/blogs/machine-learning/feed/",
    },
    {
        "company": "AWS",
        "source": "AWS Security Blog",
        "source_type": "competitor",
        "feed_url": "https://aws.amazon.com/blogs/security/feed/",
    },
    {
        "company": "OpenAI",
        "source": "OpenAI News",
        "source_type": "competitor",
        "feed_url": "https://openai.com/news/rss.xml",
    },
    {
        "company": "Anthropic",
        "source": "Anthropic News",
        "source_type": "competitor",
        "feed_url": "https://www.anthropic.com/news/rss.xml",
    },
    {
        "company": "NVIDIA",
        "source": "NVIDIA Blog",
        "source_type": "competitor",
        "feed_url": "https://blogs.nvidia.com/feed/",
    },
]


def clean_html(raw_html):
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_article_text(url):
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Mozilla/5.0 Strategic Intelligence Agent"
            }
        )

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        article = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=re.compile("content|article|post", re.I))
        )

        if article:
            text = article.get_text(separator=" ")
        else:
            text = soup.get_text(separator=" ")

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    except Exception:
        return ""


def load_existing_documents():
    if not RAW_DOCUMENTS_PATH.exists():
        return []

    with open(RAW_DOCUMENTS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_documents(documents):
    RAW_DOCUMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_DOCUMENTS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            documents,
            file,
            indent=4,
            ensure_ascii=False
        )


def build_existing_url_set(documents):
    urls = set()

    for doc in documents:
        url = doc.get("url", "")
        if url:
            urls.add(url)

    return urls


def collect_feed_documents(feed_config, existing_urls):
    company = feed_config["company"]
    source = feed_config["source"]
    source_type = feed_config["source_type"]
    feed_url = feed_config["feed_url"]

    print(f"\nCollecting: {source}")
    print(f"Feed: {feed_url}")

    feed = feedparser.parse(feed_url)

    collected = []

    for entry in feed.entries[:MAX_ITEMS_PER_FEED]:
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        published = (
            entry.get("published", "")
            or entry.get("updated", "")
            or ""
        )

        if not title or not url:
            continue

        if url in existing_urls:
            continue

        summary = clean_html(
            entry.get("summary", "")
            or entry.get("description", "")
            or ""
        )

        full_content = extract_article_text(url)

        if full_content and len(full_content) > 500:
            content = full_content
            extraction_type = "full_article"
        else:
            content = summary
            extraction_type = "rss_summary"

        if not content or len(content) < 100:
            continue

        doc = {
            "title": title,
            "source": source,
            "source_type": source_type,
            "company": company,
            "competitor": company,
            "url": url,
            "published": published,
            "content": content,
            "summary": summary,
            "content_length": len(content),
            "extraction_type": extraction_type,
        }

        collected.append(doc)
        existing_urls.add(url)

    print(f"Collected from {source}: {len(collected)}")

    return collected


def collect_competitor_sources():
    existing_documents = load_existing_documents()
    existing_urls = build_existing_url_set(existing_documents)

    print("=" * 80)
    print("COMPETITOR SOURCE COLLECTION")
    print("=" * 80)
    print(f"Existing documents: {len(existing_documents)}")

    new_documents = []

    for feed_config in COMPETITOR_FEEDS:
        docs = collect_feed_documents(
            feed_config,
            existing_urls
        )

        new_documents.extend(docs)

    all_documents = existing_documents + new_documents

    save_documents(all_documents)

    print("\n" + "=" * 80)
    print("COMPETITOR COLLECTION COMPLETED")
    print("=" * 80)
    print(f"New competitor documents: {len(new_documents)}")
    print(f"Total raw documents now: {len(all_documents)}")
    print(f"Saved to: {RAW_DOCUMENTS_PATH}")

    company_counts = {}

    for doc in all_documents:
        company = doc.get("company") or doc.get("competitor") or "Microsoft"
        company_counts[company] = company_counts.get(company, 0) + 1

    print("\nDocuments by company:")
    for company, count in sorted(company_counts.items()):
        print(f"{company}: {count}")


if __name__ == "__main__":
    collect_competitor_sources()