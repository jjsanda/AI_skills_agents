#!/usr/bin/env python3
"""Web research helper.

With no API key set, prints the structured manual research workflow (the safe,
offline default used in tests/CI). With ``WEB_RESEARCH_API_KEY`` set, it performs
a real web search over HTTPS using a Brave-compatible Search API and prints the
top results. It only touches the network when a key is explicitly provided.
"""

from __future__ import annotations

import argparse
import json
import os

MANUAL_FLOW = """\
Manual research workflow
========================
1. Frame the question precisely (scope, time range, region).
2. Gather several INDEPENDENT sources (not copies of one story).
3. Evaluate each source with references/source-quality.md
   (authority, evidence, recency, independence, bias).
4. Triangulate: treat a claim as established only when >=2 independent,
   credible sources agree; flag disagreements.
5. Synthesize into the template below, citing every claim.

Output template
---------------
# <Topic>
## Summary (3-5 sentences)
## Key findings
- <finding> [source: <url>, <date>, <credibility>]
## Open questions / disagreements
## Sources
1. <title> - <url> (<publisher>, <date>)
"""


def manual_flow(query: str) -> str:
    """Return the manual research workflow text for ``query``."""
    return f"Topic: {query}\n\n{MANUAL_FLOW}"


def online_search(query: str, api_key: str, api_url: str, max_results: int) -> str:
    """Query a Brave-compatible Search API and format the top results."""
    import urllib.parse
    import urllib.request

    url = f"{api_url}?{urllib.parse.urlencode({'q': query, 'count': max_results})}"
    request = urllib.request.Request(
        url, headers={"X-Subscription-Token": api_key, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    results = payload.get("web", {}).get("results", [])[:max_results]
    if not results:
        return f"No results for: {query}"
    lines = [f"Top {len(results)} results for: {query}", ""]
    for index, item in enumerate(results, start=1):
        lines.append(f"{index}. {item.get('title', '(untitled)')}")
        lines.append(f"   {item.get('url', '')}")
        if item.get("description"):
            lines.append(f"   {item['description']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research a topic. Prints a manual workflow unless a search API key is set.",
    )
    parser.add_argument("query", help="The research topic or question")
    parser.add_argument("--max-results", type=int, default=5, help="Max results in live mode")
    args = parser.parse_args(argv)

    api_key = os.environ.get("WEB_RESEARCH_API_KEY")
    if not api_key:
        print(manual_flow(args.query))
        return 0

    api_url = os.environ.get(
        "WEB_RESEARCH_API_URL", "https://api.search.brave.com/res/v1/web/search"
    )
    try:
        print(online_search(args.query, api_key, api_url, args.max_results))
    except Exception as exc:  # graceful fallback on any network/parse error
        print(f"Search failed ({exc}); falling back to the manual workflow.\n")
        print(manual_flow(args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
