import feedparser
from datetime import datetime
from utils.article_extract import fetch_article_text


def collect_security_blog():

    rss_url = "https://www.microsoft.com/en-us/security/blog/feed/"
    feed = feedparser.parse(rss_url)

    documents = []

    for entry in feed.entries[:100]:
        url = entry.get("link", "")
        summary = entry.get("summary", "")

        article_text = fetch_article_text(url)
        content = article_text if article_text else summary

        documents.append({
            "title": entry.get("title", ""),
            "source": "Microsoft Security Blog",
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