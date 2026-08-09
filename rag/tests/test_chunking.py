from rag.store import split_by_headings


def test_chunks_keep_heading_and_source():
    markdown = "# Authentication\n\nUse Bearer token.\n\n## Estimate\n\nCall the estimate endpoint."

    chunks = split_by_headings(markdown, "https://example.test/docs", max_chars=30)

    assert len(chunks) >= 2
    assert all(chunk.source_url == "https://example.test/docs" for chunk in chunks)
    assert any("Authentication" in chunk.section for chunk in chunks)
    assert any("Estimate" in chunk.section for chunk in chunks)
