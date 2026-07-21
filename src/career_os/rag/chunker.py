from __future__ import annotations

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, max_tokens: int = 300, overlap: int = 40) -> list[str]:
    """Token-aware chunker used for any long-form document (job descriptions,
    generated cover letters) that needs to be embedded in pieces."""
    tokens = _ENCODING.encode(text or "")
    if not tokens:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunks.append(_ENCODING.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start = end - overlap
    return chunks
