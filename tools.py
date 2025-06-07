import os
import subprocess
from typing import List

import requests


def search_web(query: str) -> str:
    """Return search results using the Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY environment variable is required")
    resp = requests.get(
        "https://api.tavily.com/search",
        params={"api_key": api_key, "query": query, "max_results": 5},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    # Expect data["results"] to be a list of dicts with "content" key
    results = data.get("results", [])
    return "\n".join(item.get("content", "") for item in results)


def pull_from_github(repo_url: str, dest: str = "repos") -> str:
    """Clone ``repo_url`` into ``dest`` and return the local path."""
    os.makedirs(dest, exist_ok=True)
    repo_name = os.path.basename(repo_url.rstrip("/"))
    path = os.path.join(dest, repo_name)
    if os.path.exists(path):
        return path
    subprocess.check_call(["git", "clone", "--depth", "1", repo_url, path])
    return path
