import asyncio
import re

import httpx
from bs4 import BeautifulSoup

from backend.app.config import settings

from .store import LocalChroma, split_by_headings


def public_docs_to_markdown(html: str) -> str:
    """Extract readable public documentation, excluding scripts/navigation."""
    soup = BeautifulSoup(html, "html.parser")
    for ignored in soup(["script", "style", "nav", "footer", "noscript"]):
        ignored.decompose()
    root = soup.find("main") or soup.body or soup
    lines: list[str] = []
    for node in root.find_all(["h1", "h2", "h3", "p", "li", "pre", "code"]):
        text = " ".join(node.get_text(" ", strip=True).split())
        if not text:
            continue
        prefix = {"h1": "# ", "h2": "## ", "h3": "### "}.get(node.name, "")
        lines.append(prefix + text)
    return "\n\n".join(lines)


async def fetch_docs() -> str:
    async with httpx.AsyncClient(
        timeout=30, follow_redirects=True, headers={"User-Agent": "VibeContentLab/1.0"}
    ) as client:
        response = await client.get(settings.docs_url)
        response.raise_for_status()
        return public_docs_to_markdown(response.text)


async def main() -> None:
    markdown = await fetch_docs()
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    chunks = split_by_headings(markdown, settings.docs_url)
    count = LocalChroma().index(chunks)
    print(f"Indexed {count} chunks from public documentation.")


if __name__ == "__main__":
    asyncio.run(main())
