# EKBA — local dev build

This is a **working local implementation** of the EKBA UI + a real, department-scoped
retrieval-augmented chat API, generated from the planning docs in `docs/`, `CLAUDE.md` and
`.claude/rules/`.

**Read this section before you read anything else.**

## ⚠️ About the API key you shared

The key pasted earlier in chat (`euri-5f21...`) is now exposed in plaintext in this
conversation. Your own `docs/INTEGRATIONS-EURI.md` already says the correct thing about this
situation:

> The sample key shared during development is considered **compromised** ... and must be
> revoked and replaced before any deployment.

**Rotate/revoke that key at euron.one and generate a fresh one before using this project.**
Put the new key in `backend/.env` (see below) — never in frontend code, never committed to git.
`backend/.env` is already gitignored.

## What this is, and what it deliberately is not

`docs/ARCHITECTURE.md` and `docs/TASKS.md` describe a large production system: multi-tenant
LangGraph agent, Qdrant, Supabase, AWS Cognito/EKS/S3/Secrets Manager, Terraform, CodeDeploy
blue/green, LangSmith tracing, a 20+ tool agent with sub-agents, full multimodal ingestion. That
is genuinely a multi-week build, and the repo is already set up for **Claude Code** to build it
phase-by-phase against `docs/TASKS.md` — that's what `CLAUDE.md` and `.claude/rules/` are for.

What's in this zip instead is a **real, running Phase-0/1 slice** built to the same design
system and the same contracts, so you have something you can open in VS Code today and actually
use, extend, or hand to Claude Code as a starting point:

| In `docs/ARCHITECTURE.md` | What this build actually does |
|---|---|
| Qdrant vector store | In-memory Python store with real embeddings + cosine similarity (`backend/app/rag_store.py`). Swap for Qdrant later — the interface is already shaped like it. |
| Supabase Postgres | Nothing persists across a server restart. No database yet. |
| AWS Cognito auth, JWT, RBAC | A mock local sign-in screen (name/email/department, no password) that sets an in-memory demo session. **Not real authentication.** |
| S3 raw file storage | Uploaded files are parsed to text and discarded — only extracted text is kept in memory. |
| LangGraph agent, tool router, sub-agents | A single retrieve-then-generate call to the Euri gateway. No planning loop, no tool calling, no reflection. |
| Multimodal ingestion (images/audio/video) | `.txt`, `.md`, `.csv`, `.pdf`, `.docx` only. |
| EKS, Terraform, CI/CD | None of it. This runs with `uvicorn` and `vite dev` on your machine. |

What **is** real and follows your docs closely:
- The Euri Gateway client (`backend/app/euri_client.py`) implements the verified retry/error
  rules from `docs/INTEGRATIONS-EURI.md` (500-that's-really-a-400 is permanent, not retried;
  401/403 fail immediately; branch on `tool_calls` presence not `finish_reason`).
- Authorization is enforced at retrieval time by department — a chunk outside your session's
  department is never scored or returned (`rag_store.py::search`), matching the README's
  "never returned from the vector store, not filtered from the UI" principle.
- Refusal is a first-class state end-to-end: the API returns `refusal: true` with the fixed
  message, and the UI renders it as a dedicated card, never a generic error.
- Every answer carries citations, `model_used`, tokens, estimated cost, latency and a
  `trace_id`, and the UI shows all of it.
- The frontend uses your exact design tokens from `docs/DESIGN-SYSTEM.md` (light/dark HSL/RGB
  variables, Geist Variable self-hosted fonts, `--radius`/shadow scale, dark-mode brand
  inversion) and the EKBA-specific components it calls for (citation chip/panel, refusal card,
  confidence meter, coarse agent-activity strip, mono response-metadata row).

## Running it

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set EURI_API_KEY to your NEW, rotated key
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`. Sign in with any name/email, pick a department, upload a
`.txt`/`.md`/`.pdf`/`.docx` file in **Documents**, then ask a question about it in **Chat** —
you'll get a cited answer, or an honest refusal if the department's documents don't cover it.

## Project layout

```
backend/   FastAPI app — config, Euri client, in-memory RAG store, routes
frontend/  React + TypeScript + Vite + Tailwind, matching docs/DESIGN-SYSTEM.md
docs/      Original planning docs — the source of truth for the full production build
.claude/   Rules and skills for Claude Code, unchanged from the scaffold
CLAUDE.md  How Claude Code should work in this repo
```

## Next steps toward the real thing

1. Rotate the API key (see above) before doing anything else.
2. Open this folder in **Claude Code** and work through `docs/TASKS.md` phase by phase — that's
   what the `.claude/rules/` and `CLAUDE.md` in this repo are configured for, and it's genuinely
   the right tool for standing up Qdrant, Supabase, Cognito, Terraform and the LangGraph agent
   correctly and safely.
3. Everything in `backend/app/` is written to be swapped incrementally: `rag_store.py` for a
   Qdrant client, the mock session in `frontend/src/store/useAppStore.ts` for real Cognito, the
   single chat call in `routes/chat.py` for the full planner/tool-router/reflector loop.
