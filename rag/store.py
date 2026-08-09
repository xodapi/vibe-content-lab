import re
from collections.abc import Iterable
from dataclasses import dataclass

import chromadb
from openai import OpenAI

from backend.app.config import settings

COLLECTION_NAME = "vibe_public_agent_api"


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    section: str
    source_url: str


def split_by_headings(markdown: str, source_url: str, max_chars: int = 1400) -> list[Chunk]:
    """Keeps headings in each chunk, so citations retain useful context."""
    sections = re.split(r"(?=^#{1,3}\s)", markdown, flags=re.MULTILINE)
    chunks: list[Chunk] = []
    for section_index, section in enumerate(sections):
        section = re.sub(r"\s+", " ", section).strip()
        if not section:
            continue
        heading = section.split(" ", 2)[:2]
        title = " ".join(heading)
        for part_index, start in enumerate(range(0, len(section), max_chars)):
            text = section[start : start + max_chars]
            if start:
                text = f"{title}. {text}"
            chunks.append(
                Chunk(
                    id=f"doc-{section_index}-{part_index}",
                    text=text,
                    section=title[:180],
                    source_url=source_url,
                )
            )
    return chunks


class LocalChroma:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
        self.openai = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def _embed(self, texts: Iterable[str]) -> list[list[float]]:
        if not self.openai:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings")
        return [
            item.embedding
            for item in self.openai.embeddings.create(
                model="text-embedding-3-small", input=list(texts)
            ).data
        ]

    def index(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {"section": chunk.section, "source_url": chunk.source_url} for chunk in chunks
            ],
            embeddings=self._embed(chunk.text for chunk in chunks),
        )
        return len(chunks)

    def search(self, question: str, limit: int = 4) -> list[dict]:
        result = self.collection.query(
            query_embeddings=self._embed([question]),
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "text": document,
                "section": metadata["section"],
                "source_url": metadata["source_url"],
                "distance": distance,
            }
            for document, metadata, distance in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0], strict=False
            )
        ]
