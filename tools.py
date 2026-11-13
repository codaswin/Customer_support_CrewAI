from datetime import datetime
from pathlib import Path

from crewai.tools import tool
from ddgs import DDGS

import kb

LOG_FILE = Path(__file__).parent / "logs" / "gap_log.txt"


@tool("Knowledge Base Search")
def kb_search(query: str) -> str:
    """Search the company documents. Returns relevant passages, or NOT_FOUND if they don't cover the query."""
    return kb.search(query)


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the internet. Returns the top results as title, URL and snippet."""
    results = DDGS().text(query, max_results=5)
    return "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results) or "NO_RESULTS"


@tool("Gap Log Writer")
def log_gap(query: str, web_searched: bool) -> str:
    """Record a customer query that needed web search. Set web_searched=False to skip logging."""
    if not web_searched:
        return "Skipped: no web search was used."
    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} | {query.replace(chr(10), ' ')}\n")
    return "Logged."
