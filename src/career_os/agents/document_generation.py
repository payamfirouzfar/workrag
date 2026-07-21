from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from ..rag.retriever import ProfileRAG
from ..core.exceptions import UnverifiedClaimError
from ..llm.factory import get_chat_model

COVER_LETTER_SYSTEM = """You write cover letters using ONLY facts supplied in
CONTEXT (retrieved from the candidate's verified profile). Never invent
metrics, employers, dates, or skills that are not in CONTEXT. If a strong
argument requires a fact not present in CONTEXT, omit it rather than
inventing it."""

COVER_LETTER_USER = """JOB: {title} at {company}

STRATEGY:
{strategy}

VERIFIED CONTEXT FROM CANDIDATE PROFILE:
{context}

Write a concise, specific cover letter (under 350 words)."""


class DocumentGenerationAgent:
    """Generates cover letters (and, in a full build, tailored resume
    variants) strictly from Profile RAG evidence -- every generated
    document is followed by a claim-verification pass."""

    def __init__(self, profile_rag: ProfileRAG):
        self.rag = profile_rag
        self.llm = get_chat_model(temperature=0.4)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", COVER_LETTER_SYSTEM),
            ("human", COVER_LETTER_USER),
        ])

    async def generate_cover_letter(self, job: dict, strategy: dict) -> dict:
        evidence = await self.rag.retrieve(
            f"experience and skills relevant to {job['title']} at {job['company']}",
            k=8,
        )
        context = "\n".join(f"- {e['text']}" for e in evidence)

        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "title": job["title"],
            "company": job["company"],
            "strategy": "\n".join(strategy.get("talking_points", [])),
            "context": context or "(no evidence retrieved)",
        })
        letter = response.content

        verification = await self._verify_sentences(letter)

        return {
            "cover_letter": letter,
            "evidence_used": evidence,
            "verification": verification,
        }

    async def _verify_sentences(self, letter: str) -> list[dict]:
        """Best-effort per-sentence grounding check -- flags sentences that
        don't find supporting evidence rather than silently trusting the LLM."""
        results = []
        for sentence in [s.strip() for s in letter.split(".") if s.strip()]:
            check = await self.rag.verify_claim(sentence)
            results.append({"sentence": sentence, **check})
        return results

    async def require_verified_document(self, job: dict, strategy: dict) -> dict:
        doc = await self.generate_cover_letter(job, strategy)
        unverified = [v for v in doc["verification"] if not v["verified"]]
        if len(unverified) > max(1, len(doc["verification"]) // 3):
            raise UnverifiedClaimError(
                f"Cover letter has {len(unverified)} unverified claims out of "
                f"{len(doc['verification'])} -- regenerate or edit before use."
            )
        return doc
