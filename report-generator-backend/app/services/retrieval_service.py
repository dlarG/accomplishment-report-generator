
import re

from app.database.knowledge_repository import get_all_reports, get_report


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in",
    "on", "at", "for", "with", "from", "by", "as", "is",
    "was", "were", "are", "be", "been", "being", "this",
    "that", "these", "those", "it", "its", "their", "his",
    "her", "they", "them", "he", "she", "we", "our", "i",
    "me", "my", "you", "your", "who", "which", "what",
    "when", "where", "how", "have", "has", "had"
}


def tokenize(text: str) -> set[str]:
    """Convert text into lowercase keywords."""

    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {
        word for word in words
        if word not in STOPWORDS and len(word) > 2
    }


def retrieve_relevant_examples(
    query: str,
    limit: int = 5
) -> list[dict]:
    """
    Find historical accomplishment statements that share
    keywords with the current user's input.

    Historical reports are used only as writing references.
    They must not be treated as current activities.
    """

    query_keywords = tokenize(query)

    if not query_keywords:
        return []

    reports = get_all_reports()
    matches = []

    for report in reports:
        full_report = get_report(report["id"])

        if not full_report:
            continue

        extracted_text = full_report.get("extracted_text", "")

        # Evaluate individual lines as separate examples.
        lines = [
            line.strip()
            for line in extracted_text.splitlines()
            if line.strip()
        ]

        for line in lines:
            line_keywords = tokenize(line)

            if not line_keywords:
                continue

            common_keywords = query_keywords.intersection(line_keywords)

            if not common_keywords:
                continue

            score = len(common_keywords) / len(query_keywords)

            matches.append({
                "filename": report["filename"],
                "text": line,
                "score": round(score, 3),
                "matched_keywords": sorted(common_keywords)
            })

    # Highest keyword similarity first.
    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return matches[:limit]
