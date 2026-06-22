import feedparser
from datetime import datetime
from utils.article_extract import fetch_article_text


def collect_extra_sources():

    feeds = {
        "Microsoft Research": "https://www.microsoft.com/en-us/research/feed/",
        "Windows Blog": "https://blogs.windows.com/feed/",
        "Microsoft Developer Blog": "https://devblogs.microsoft.com/feed/",
        "GitHub Blog": "https://github.blog/feed/",
        "Azure AI Foundry Blog": "https://techcommunity.microsoft.com/t5/azure-ai-foundry-blog/bg-p/AzureAIBlog/rss",
        "Microsoft 365 Blog": "https://www.microsoft.com/en-us/microsoft-365/blog/feed/",
        "Power Platform Blog": "https://www.microsoft.com/en-us/power-platform/blog/feed/",

        # Extra Tech Community sources
        "Microsoft AI Blog": "https://techcommunity.microsoft.com/t5/ai-ai-platform-blog/bg-p/AIPlatformBlog/rss",
        "Microsoft Azure Blog Community": "https://techcommunity.microsoft.com/t5/azure/bg-p/Azure/rss",
        "Microsoft Security Community": "https://techcommunity.microsoft.com/t5/security-compliance-and-identity/bg-p/security-compliance-identity/rss",
        "Microsoft 365 Community": "https://techcommunity.microsoft.com/t5/microsoft-365-blog/bg-p/microsoft_365blog/rss",
        "Microsoft Teams Blog": "https://techcommunity.microsoft.com/t5/microsoft-teams-blog/bg-p/MicrosoftTeamsBlog/rss",
        "Microsoft Copilot Blog": "https://techcommunity.microsoft.com/t5/microsoft-365-copilot-blog/bg-p/Microsoft365CopilotBlog/rss",
        "Azure Architecture Blog": "https://techcommunity.microsoft.com/t5/azure-architecture-blog/bg-p/AzureArchitectureBlog/rss",
        "Data and AI Blog": "https://techcommunity.microsoft.com/t5/azure-data-blog/bg-p/AzureDataBlog/rss",
    }

    documents = []

    for source_name, rss_url in feeds.items():
        print(f"\nCollecting from {source_name}...")

        try:
            feed = feedparser.parse(rss_url)
            print(f"Available articles: {len(feed.entries)}")

            for entry in feed.entries[:100]:
                url = entry.get("link", "")
                summary = entry.get("summary", "")

                article_text = fetch_article_text(url)
                content = article_text if article_text else summary

                documents.append({
                    "title": entry.get("title", ""),
                    "source": source_name,
                    "source_type": "official_or_related",
                    "url": url,
                    "published": entry.get("published", ""),
                    "content": content,
                    "summary": summary,
                    "content_length": len(content),
                    "used_full_article": bool(article_text),
                    "collected_at": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Error collecting {source_name}: {e}")

    return documents


if __name__ == "__main__":
    docs = collect_extra_sources()

    print("\nResults")
    print("-" * 50)
    print(f"Total extra documents collected: {len(docs)}")

    full_articles = sum(1 for doc in docs if doc.get("used_full_article"))
    print(f"Full articles extracted: {full_articles}")