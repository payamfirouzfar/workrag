from __future__ import annotations

from langchain_community.vectorstores import PGVector

from ..config import get_settings
from .embeddings import get_embeddings_client

SETTINGS = get_settings()


def get_profile_vectorstore(user_id: str) -> PGVector:
    """One PGVector collection per user — keeps embeddings isolated so a
    retrieval query can never leak another user's profile data."""
    return PGVector(
        connection_string=SETTINGS.database_url,
        embedding_function=get_embeddings_client(),
        collection_name=f"profile_{user_id}",
    )
