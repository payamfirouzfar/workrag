from __future__ import annotations

from ..config import get_settings

SETTINGS = get_settings()


def get_chat_model(temperature: float = 0.0):
    """Returns a LangChain chat model. Defaults to a free, local Ollama
    model (LLM_PROVIDER=ollama, the default) -- no API key, no per-token
    cost. Set LLM_PROVIDER=openai in .env to use a paid OpenAI model
    instead; nothing else in the codebase needs to change.

    [MANUAL ACTION REQUIRED] Install Ollama (https://ollama.com) and run
    `ollama pull llama3.1` before first use of the default provider.
    """
    if SETTINGS.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=SETTINGS.llm_model, temperature=temperature,
                          api_key=SETTINGS.openai_api_key)

    from langchain_ollama import ChatOllama

    return ChatOllama(model=SETTINGS.ollama_llm_model, temperature=temperature,
                      base_url=SETTINGS.ollama_base_url)


def get_embeddings_client():
    """Returns a LangChain embeddings client. Defaults to the free, local
    `nomic-embed-text` model served by Ollama. Set LLM_PROVIDER=openai to
    use OpenAI's paid embeddings instead.

    [MANUAL ACTION REQUIRED] `ollama pull nomic-embed-text` before first use
    of the default provider. If you switch providers after jobs/profiles
    have already been embedded, re-embed existing data -- vector dimensions
    and semantics differ between providers.
    """
    if SETTINGS.llm_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=SETTINGS.embedding_model, api_key=SETTINGS.openai_api_key)

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(model=SETTINGS.ollama_embedding_model, base_url=SETTINGS.ollama_base_url)
