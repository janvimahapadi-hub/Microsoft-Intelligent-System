import json


CLEANED_PATH = "data/cleaned_documents.json"


def remove_duplicates(documents):
    seen = set()
    unique_documents = []

    for doc in documents:
        title = doc.get("title", "").lower().strip()
        url = doc.get("url", "").strip()

        key = (title, url)

        if key not in seen:
            seen.add(key)
            unique_documents.append(doc)

    return unique_documents


def main():
    with open(CLEANED_PATH, "r", encoding="utf-8") as file:
        documents = json.load(file)

    unique_documents = remove_duplicates(documents)

    with open(CLEANED_PATH, "w", encoding="utf-8") as file:
        json.dump(unique_documents, file, indent=4, ensure_ascii=False)

    print(f"Before deduplication: {len(documents)}")
    print(f"After deduplication: {len(unique_documents)}")
    print(f"Saved to: {CLEANED_PATH}")


if __name__ == "__main__":
    main()