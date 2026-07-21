from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from ..config import get_settings

SETTINGS = get_settings()


def get_embeddings_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=SETTINGS.embedding_model, api_key=SETTINGS.openai_api_key)
