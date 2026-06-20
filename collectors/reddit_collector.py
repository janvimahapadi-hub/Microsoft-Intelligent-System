import feedparser
from datetime import datetime
from bs4 import BeautifulSoup


def clean_html(text):

    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)


def collect_reddit():

    subreddits = ["Microsoft", "Azure", "sysadmin", "cybersecurity", "artificial"]

    documents = []

    for subreddit in subreddits:

        rss_url = f"https://www.reddit.com/r/{subreddit}/.rss"

        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:100]:

            documents.append({
                "title": entry.get("title", ""),
                "source": f"Reddit-{subreddit}",
                "source_type": "community",
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "content": clean_html(
                    entry.get("summary", "")
                ),
                "collected_at": datetime.now().isoformat()
            })

    return documents