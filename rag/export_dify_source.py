"""Export a clean, public-documentation-only Markdown source for Dify upload."""

import asyncio
from pathlib import Path

from .ingest import fetch_docs


async def main() -> None:
    text = await fetch_docs()
    target = Path(__file__).parents[1] / "dify" / "vibemarketolog-public-agent-api.md"
    target.write_text(
        "# Public Agent API documentation source\n\n"
        "Source: https://lk.vibemarketolog.ru/docs/agent-api\n\n"
        + text,
        encoding="utf-8",
    )
    print(f"Wrote {target}")


if __name__ == "__main__":
    asyncio.run(main())
