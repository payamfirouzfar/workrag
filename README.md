# AI Career OS

An agentic system that ingests your resume, builds a verified profile (RAG-backed,
provenance-tagged), discovers jobs from legitimate sources, matches and ranks them
against your profile, generates tailored application documents, and — only with
explicit human approval at every irreversible step — assists with submitting
applications through a safety-controlled browser automation layer.

## ⚠️ Status of this delivery

This repository ships **Phases 1–4 + the security core + the source adapter
framework + the human-approval-gate skeleton + tests**.

- **Browser automation (Phase 5)** is stubbed: the *safety controller is fully
  implemented* (CAPTCHA/MFA/anti-bot detection, sensitive-field gating, and a
  hard "no submit without recorded user approval" gate), but the Playwright
  driving logic itself is a scaffold you'll need to finish and test against
  real ATS forms.
- **Email intelligence (Phase 7)** ships with the OAuth scaffold + classifier
  hooks only.
- Anything marked `[MANUAL ACTION REQUIRED]` below needs you.

## [MANUAL ACTION REQUIRED] Before running

1. Drop your resume into `data/cv/your_resume.pdf` (or upload later via
   `POST /profile/upload-cv` once the API is running).
2. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` at minimum.
3. `docker compose up --build`

## Directory structure

```
ai-career-os/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
├── alembic.ini
├── data/
│   ├── cv/                 # <-- put your resume here
│   └── uploads/
├── src/career_os/
│   ├── config.py
│   ├── main.py
│   ├── core/{logging,audit,exceptions}.py
│   ├── db/{base,session,models}.py
│   ├── schemas/{profile,job,application,email}.py
│   ├── rag/{embeddings,vectorstore,chunker,retriever}.py
│   ├── agents/{orchestrator,profile_ingestion,profile_rag,job_discovery,
│   │           job_extraction,job_matching,job_verification,job_dedup,
│   │           job_ranking,application_strategy,document_generation,
│   │           browser_application}.py
│   ├── sources/{policy,base,greenhouse,lever,workday,ashby,rss}.py
│   ├── browser/{session,field_mapping,safety}.py
│   ├── email/{oauth,classifier}.py
│   ├── security/{prompt_injection,content_sanitizer,url_safety}.py
│   └── api/{routes_profile,routes_jobs,routes_applications,
│             routes_email,routes_approval}.py
└── tests/{conftest,test_profile_ingestion,test_job_matching,
            test_job_verification,test_prompt_injection,
            test_browser_field_mapping}.py
```

## Safety principles baked into the code

- **Provenance taxonomy**: every fact about you is tagged `CONFIRMED_FACT`,
  `INFERRED_SKILL`, `POSSIBLE_SKILL`, or `MISSING_INFORMATION` — the system
  never invents experience.
- **Prompt-injection defense**: all external content (job descriptions, emails,
  web pages) is sanitized before reaching an LLM (`security/prompt_injection.py`).
- **URL/phishing verification** before any application link is trusted
  (`security/url_safety.py`).
- **Human approval gate**: `BrowserApplicationAgent.submit()` raises
  `PermissionError` if called without a recorded `UserApproval` row — there is
  no code path that submits an application without your explicit sign-off.
