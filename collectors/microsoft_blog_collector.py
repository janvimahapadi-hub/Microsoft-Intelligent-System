import feedparser
from datetime import datetime
from utils.article_extract import fetch_article_text


def collect_microsoft_blog():

    rss_url = "https://blogs.microsoft.com/feed/"
    feed = feedparser.parse(rss_url)

    documents = []

    for entry in feed.entries[:100]:
        url = entry.get("link", "")
        summary = entry.get("summary", "")

        article_text = fetch_article_text(url)
        content = article_text if article_text else summary

        documents.append({
            "title": entry.get("title", ""),
            "source": "Microsoft Blog",
            "source_type": "official",
            "url": url,
            "published": entry.get("published", ""),
            "content": content,
            "summary": summary,
            "content_length": len(content),
            "used_full_article": bool(article_text),
            "collected_at": datetime.now().isoformat()
        })

    return documents