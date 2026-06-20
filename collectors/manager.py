import json
import os
from collectors.extra_sources_collector import collect_extra_sources
from collectors.microsoft_blog_collector import collect_microsoft_blog
from collectors.azure_blog_collector import collect_azure_blog
from collectors.security_blog_collector import collect_security_blog
from collectors.reddit_collector import collect_reddit


RAW_PATH = "data/raw_documents.json"


def save_documents(documents):
    os.makedirs("data", exist_ok=True)

    with open(RAW_PATH, "w", encoding="utf-8") as file:
        json.dump(documents, file, indent=4, ensure_ascii=False)


def collect_all():
    print("Collecting Microsoft Blog articles...")
    microsoft_docs = collect_microsoft_blog()

    print("Collecting Azure Blog articles...")
    azure_docs = collect_azure_blog()

    print("Collecting Microsoft Security Blog articles...")
    security_docs = collect_security_blog()

    print("Collecting Reddit posts...")
    reddit_docs = collect_reddit()
    print("Collecting extra Microsoft-related sources...")
    extra_docs = collect_extra_sources() 

    all_documents = (
    microsoft_docs
    + azure_docs
    + security_docs
    + reddit_docs
    + extra_docs
)

    save_documents(all_documents)

    print("\nCollection completed")
    print(f"Microsoft Blog: {len(microsoft_docs)}")
    print(f"Azure Blog: {len(azure_docs)}")
    print(f"Security Blog: {len(security_docs)}")
    print(f"Reddit: {len(reddit_docs)}")
    print(f"Total documents: {len(all_documents)}")
    print(f"Saved to: {RAW_PATH}")
    print(f"Extra sources: {len(extra_docs)}")

    full_articles = sum(
        1 for doc in all_documents
        if doc.get("used_full_article") is True
    )

    print(f"Full articles extracted: {full_articles}")


if __name__ == "__main__":
    collect_all()