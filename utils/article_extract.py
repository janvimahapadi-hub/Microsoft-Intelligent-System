import requests
from bs4 import BeautifulSoup
import trafilatura


def fetch_with_trafilatura(url):
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False
    )

    if not text:
        return ""

    text = " ".join(text.split())
    return text if len(text) > 500 else ""


def fetch_with_beautifulsoup(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    paragraphs = soup.find_all("p")

    text = " ".join(
        p.get_text(" ", strip=True)
        for p in paragraphs
    )

    text = " ".join(text.split())

    bad_words = [
        "we use cookies",
        "accept all",
        "reject all",
        "manage cookies",
        "privacy statement"
    ]

    if any(word in text.lower() for word in bad_words):
        return ""

    return text if len(text) > 500 else ""


def fetch_article_text(url):
    try:
        text = fetch_with_trafilatura(url)
        if text:
            return text

        text = fetch_with_beautifulsoup(url)
        if text:
            return text

        return ""

    except Exception:
        return ""