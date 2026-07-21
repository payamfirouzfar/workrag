from __future__ import annotations
import uuid

from ..rag.retriever import ProfileRAG
from .profile_ingestion import ParsedProfile


class ProfileRAGAgent:
    """Thin orchestration layer: ingests a ParsedProfile's chunks into the
    user's ProfileRAG and exposes claim verification to downstream agents
    (document generation, form filling) so nothing they write about the
    user goes unverified."""

    def __init__(self, user_id: uuid.UUID):
        self.user_id = user_id
        self.rag = ProfileRAG(user_id)

    async def index_profile(self, parsed: ParsedProfile) -> int:
        await self.rag.add_chunks(parsed.chunks)
        return len(parsed.chunks)

    async def verify(self, claim: str) -> dict:
        return await self.rag.verify_claim(claim)

    async def search(self, query: str, k: int = 6) -> list[dict]:
        return await self.rag.retrieve(query, k=k)
