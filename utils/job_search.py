"""
job_search.py  –  Real-time job search using DuckDuckGo (no API key needed).

Fetches actual search result snippets for each inferred role so the LLM
can extract real company names and URLs instead of hallucinating them.
"""
import time

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


_JOB_DOMAINS = [
    "linkedin.com/jobs",
    "indeed.com/viewjob",
    "indeed.com/jobs",
    "naukri.com",
    "glassdoor.com/job",
    "internshala.com",
    "wellfound.com/jobs",
    "careers.",
    "/jobs/",
    "/careers/",
    "jobs.lever.co",
    "boards.greenhouse.io",
    "workatastartup.com",
]


def _is_job_link(url: str) -> bool:
    return any(d in url for d in _JOB_DOMAINS)


def search_jobs_for_role(role: str, max_results: int = 4) -> list[dict]:
    """
    Search DuckDuckGo for real job postings for a given role.
    Returns a list of dicts: {title, url, snippet, is_job_board}
    Tries multiple query variations for resilience.
    """
    queries = [
        f'"{role}" internship OR "entry level" job apply 2025',
        f'"{role}" junior job opening site:linkedin.com OR site:naukri.com OR site:indeed.com',
        f'"{role}" fresher OR graduate job 2025',
        f"{role} job openings entry level",
    ]

    results = []
    seen_urls = set()

    try:
        ddgs = DDGS()
        for query in queries:
            try:
                hits = list(ddgs.text(query, max_results=max_results))
                for h in hits:
                    url = h.get("href") or h.get("url") or ""
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    results.append({
                        "title": h.get("title", ""),
                        "url": url,
                        "snippet": h.get("body", "")[:250],
                        "is_job_board": _is_job_link(url),
                    })
                time.sleep(0.3)
                if len(results) >= max_results:
                    break
            except Exception:
                time.sleep(0.5)
                continue
    except Exception:
        pass

    # Prefer actual job-board links
    results.sort(key=lambda x: not x["is_job_board"])
    return results[:max_results]


def _linkedin_search_url(role: str) -> str:
    """Construct a guaranteed-working LinkedIn search URL (not a specific job page)."""
    encoded = role.strip().replace(" ", "%20")
    return f"https://www.linkedin.com/jobs/search/?keywords={encoded}&f_E=1%2C2&sortBy=DD"


def fetch_real_job_snippets(roles: list[str]) -> str:
    """
    Given a list of role names, searches DuckDuckGo for each role and returns
    a formatted string of real search results to embed in the LLM prompt.
    Each role is guaranteed to have at least a LinkedIn search fallback URL.
    """
    output_lines = ["=== REAL JOB SEARCH RESULTS (fetched live from DuckDuckGo) ===\n"]

    for role in roles:
        output_lines.append(f"## Role: {role}")
        results = search_jobs_for_role(role, max_results=3)

        if results:
            for i, r in enumerate(results, 1):
                output_lines.append(f"  [{i}] Title: {r['title']}")
                output_lines.append(f"       URL: {r['url']}")
                output_lines.append(f"       Snippet: {r['snippet']}")
        else:
            # Guaranteed fallback: LinkedIn search (always works, not a fake job page)
            fallback_url = _linkedin_search_url(role)
            output_lines.append(f"  [1] Title: {role} Jobs - LinkedIn Search")
            output_lines.append(f"       URL: {fallback_url}")
            output_lines.append(f"       Snippet: Search LinkedIn for '{role}' entry-level positions. Filter by date posted.")

        output_lines.append("")

    return "\n".join(output_lines)
