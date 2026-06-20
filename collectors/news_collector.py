import feedparser
from datetime import datetime
from utils.article_extract import fetch_full_article


def collect_news():
    queries = [
        "Microsoft AI",
        "Microsoft Azure",
        "Microsoft Copilot",
        "Microsoft cybersecurity",
        "Microsoft cloud"
    ]

    documents = []

    for query in queries:
        rss_url = (
            f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"
            "&hl=en-US&gl=US&ceid=US:en"
        )

        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:25]:
            url = entry.get("link", "")
            summary = entry.get("summary", "")

            full_text = fetch_full_article(url)

            content = full_text if full_text else summary

            documents.append({
                "title": entry.get("title", ""),
                "source": "Google News RSS",
                "source_type": "news",
                "query": query,
                "url": url,
                "published": entry.get("published", ""),
                "content": content,
                "summary": summary,
                "collected_at": datetime.now().isoformat()
            })

    return documents


if __name__ == "__main__":
    docs = collect_news()
    print(f"Collected {len(docs)} news documents")

    full_count = sum(1 for doc in docs if len(doc["content"]) > 500)
    print(f"Documents with full content: {full_count}")

    for doc in docs[:3]:
        print("-" * 80)
        print(doc["title"])
        print("Content length:", len(doc["content"]))