# AI Career OS

AI Career OS is an experimental assistant for organising a job search. It turns a resume into a structured profile, finds and ranks relevant roles, prepares application material, and keeps a human approval step before any submission action.

The project focuses on a problem I care about: job-search tools should help with repetitive work without inventing experience or taking irreversible actions on a person's behalf.

## What is implemented

The current repository includes:

- PDF resume ingestion and chunking
- a provenance-aware profile model
- retrieval over profile information
- adapters for several public applicant-tracking-system sources
- job extraction, verification, deduplication, matching, and ranking agents
- application-strategy and document-generation components
- FastAPI routes for profiles, jobs, applications, approvals, and email classification
- PostgreSQL, pgvector, Redis, Alembic, Docker, and structured logging
- tests for profile ingestion, matching, verification, prompt-injection checks, and browser field mapping

## What is not finished

This is version `0.1.0`, not a complete automatic application platform.

- The browser safety controls and approval gate are present, but the Playwright logic that fills real application forms is still a scaffold.
- Email OAuth and classification have interface-level support, but the complete provider integration is not finished.
- Every source adapter needs real-world testing against its provider's current terms, rate limits, and page structure.

The system should not be used to submit applications unattended.

## Safety approach

- Profile statements are labelled as confirmed, inferred, possible, or missing instead of being silently invented.
- External job and email content passes through sanitisation and prompt-injection checks before reaching an LLM.
- Application URLs are checked before they are trusted.
- Submission requires a recorded user decision. The browser agent rejects an unapproved submission request.
- CAPTCHA and MFA are treated as points where the user must take control.

These controls reduce risk, but they do not make the unfinished browser automation production-ready.

## Quick start with Ollama

You need Docker and Docker Compose.

```bash
git clone https://github.com/payamfirouzfar/workrag.git
cd workrag
cp .env.example .env
docker compose up --build
```

Pull the local models once:

```bash
docker compose exec ollama ollama pull llama3.1
docker compose exec ollama ollama pull nomic-embed-text
```

Add a resume at `data/cv/your_resume.pdf`, or start the API and upload it through `POST /profile/upload-cv`.

The FastAPI health check is available at `/healthz`, and the interactive API documentation is at `/docs`.

## Optional OpenAI provider

Ollama is the default. To use OpenAI instead, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` in `.env`, use the correct embedding dimension, and install the optional dependency:

```bash
pip install -e ".[openai]"
```

## Local development

The project requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Repository guide

```text
src/career_os/agents/      workflow and specialist agents
src/career_os/api/         FastAPI routes
src/career_os/browser/     form mapping and safety controls
src/career_os/db/          database models and sessions
src/career_os/email/       OAuth and classification scaffolding
src/career_os/rag/         chunking, embeddings, retrieval, vector store
src/career_os/security/    content, prompt, and URL checks
src/career_os/sources/     job-source policies and adapters
tests/                     focused automated tests
```

## Responsible use

Review every generated document, confirm every profile claim, respect each job site's rules, and keep a person in control of submission. This repository is a work in progress and should be evaluated in a test environment before it is connected to real accounts.
