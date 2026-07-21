from __future__ import annotations
import uuid
from typing import Any

from .vectorstore import get_profile_vectorstore
from langchain_core.documents import Document


class ProfileRAG:
    """Personal knowledge base over the user's CV/experience."""

    def __init__(self, user_id: uuid.UUID):
        self.user_id = str(user_id)
        self._store = None

    def _ensure_store(self):
        if self._store is None:
            self._store = get_profile_vectorstore(self.user_id)
        return self._store

    async def add_chunks(self, chunks: list[dict]) -> None:
        store = self._ensure_store()
        docs = [
            Document(page_content=c["text"],
                     metadata={**{k: v for k, v in c.items() if k != "text"},
                               "user_id": self.user_id})
            for c in chunks
        ]
        await store.aadd_documents(docs)

    async def retrieve(self, query: str, k: int = 6,
                       provenance_filter: list[str] | None = None) -> list[dict]:
        store = self._ensure_store()
        filter_dict: dict[str, Any] = {"user_id": self.user_id}
        if provenance_filter:
            filter_dict["provenance"] = {"$in": provenance_filter}
        docs = await store.asimilarity_search_with_relevance_scores(
            query, k=k, filter=filter_dict,
        )
        return [
            {"text": d.page_content,
             "score": float(score),
             "source": d.metadata.get("source", ""),
             "doc_type": d.metadata.get("doc_type", ""),
             "provenance": d.metadata.get("provenance", "CONFIRMED_FACT"),
             "confidence": d.metadata.get("confidence", 1.0)}
            for d, score in docs
        ]

    async def verify_claim(self, claim: str) -> dict:
        """Every AI-generated statement must pass this."""
        hits = await self.retrieve(claim, k=3)
        if not hits:
            return {"verified": False, "reason": "no supporting evidence in profile",
                    "missing_information": [claim]}
        top = hits[0]
        if top["score"] < 0.55:
            return {"verified": False,
                    "reason": f"low confidence ({top['score']:.2f})",
                    "missing_information": [claim]}
        return {"verified": True, "evidence": top, "confidence": top["score"]}
