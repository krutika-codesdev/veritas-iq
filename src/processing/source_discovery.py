from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

import requests


@dataclass
class SourceCandidate:
    url: str
    title: str = ""
    source_type: str = ""
    score: int = 0


SEARCH_URL = "https://html.duckduckgo.com/html/"


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _source_type(url: str) -> str:
    domain = _domain(url)

    if "3m.com" in domain:
        return "manufacturer"

    if any(
        domain.endswith(domain_name)
        for domain_name in [
            "grainger.com",
            "mcmaster.com",
        ]
    ):
        return "industrial_distributor"

    if any(
        word in domain
        for word in [
            "supply",
            "industrial",
            "tool",
            "equipment",
        ]
    ):
        return "distributor"

    return "other"


def rank_source(
    url: str,
    title: str,
    mpn: str,
    description: str,
) -> int:
    """
    Rank a discovered source.

    Higher score means a better candidate.
    """

    score = 0

    domain = _domain(url)
    text = f"{url} {title}".lower()

    mpn_lower = mpn.lower()
    description_lower = description.lower()

    # Exact MPN is the strongest signal.
    if mpn_lower in text:
        score += 50

    # Also reward individual MPN components.
    mpn_parts = [
        part
        for part in re.split(r"[-_\s]+", mpn_lower)
        if len(part) >= 3
    ]

    for part in mpn_parts:
        if part in text:
            score += 5

    # Manufacturer sources are preferred.
    if domain.endswith("3m.com"):
        score += 40

    # Known authoritative industrial sources.
    if domain.endswith("grainger.com"):
        score += 25

    if domain.endswith("mcmaster.com"):
        score += 25

    # Distributor signals.
    if any(
        word in domain
        for word in [
            "supply",
            "industrial",
            "tool",
            "equipment",
        ]
    ):
        score += 10

    # Product/technical source signals.
    for keyword in [
        "product",
        "technical",
        "specification",
        "spec",
        "manual",
        "datasheet",
        "catalog",
        "abrasive",
        "sanding",
    ]:
        if keyword in text:
            score += 3

    # Description signals.
    description_terms = [
        term
        for term in re.findall(
            r"[a-z0-9]+",
            description_lower,
        )
        if len(term) >= 4
    ]

    for term in description_terms:
        if term in text:
            score += 1

    # Penalize marketplaces.
    for marketplace in [
        "amazon.",
        "ebay.",
        "walmart.",
        "aliexpress.",
    ]:
        if marketplace in domain:
            score -= 30

    return score


def _extract_search_results(
    html: str,
) -> list[tuple[str, str]]:
    """
    Extract result URLs and titles from DuckDuckGo HTML.
    """

    results: list[tuple[str, str]] = []

    # DuckDuckGo result links commonly appear as:
    # <a rel="nofollow" class="result__a" href="...">Title</a>
    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )

    for match in pattern.finditer(html):
        raw_url = unquote(match.group(1))
        raw_title = re.sub(
            r"<[^>]+>",
            "",
            match.group(2),
        ).strip()

        if raw_url.startswith("//"):
            raw_url = "https:" + raw_url

        if not raw_url.startswith("http"):
            continue

        results.append(
            (
                raw_url,
                raw_title,
            )
        )

    return results


def discover_sources(
    mpn: str,
    description: str,
    max_results: int = 5,
) -> list[SourceCandidate]:
    """
    Discover candidate product sources.

    Uses a lightweight public search endpoint.
    This is intentionally small and does not crawl the web.
    """

    queries = [
        f'"{mpn}"',
        f'"{mpn}" "{description}"',
    ]

    candidates: dict[str, SourceCandidate] = {}

    for query in queries:
        try:
            response = requests.get(
                SEARCH_URL,
                params={"q": query},
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/151 Safari/537.36"
                    )
                },
                timeout=15,
            )

            response.raise_for_status()

        except requests.RequestException:
            continue

        for url, title in _extract_search_results(
            response.text
        ):
            domain = _domain(url)

            if not domain:
                continue

            if "duckduckgo.com" in domain:
                continue

            score = rank_source(
                url=url,
                title=title,
                mpn=mpn,
                description=description,
            )

            candidate = SourceCandidate(
                url=url,
                title=title,
                source_type=_source_type(url),
                score=score,
            )

            existing = candidates.get(url)

            if (
                existing is None
                or candidate.score > existing.score
            ):
                candidates[url] = candidate

    ranked = sorted(
        candidates.values(),
        key=lambda item: item.score,
        reverse=True,
    )

    return ranked[:max_results]


def retrieve_source(
    url: str,
    timeout: int = 15,
) -> str | None:
    """
    Retrieve HTML/text content from a discovered source.
    """

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151 Safari/537.36"
                )
            },
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if not (
            "text" in content_type
            or "html" in content_type
            or "json" in content_type
        ):
            return None

        return response.text

    except requests.RequestException:
        return None