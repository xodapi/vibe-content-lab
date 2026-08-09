# Vibe Content Lab

Portfolio-grade internal AI tool for a public API documentation corpus. It demonstrates a complete applied-AI delivery path: **RAG, embeddings, local vector search, retrieval evaluation, FastAPI, React, n8n, Dify, Docker, logs, webhooks and human approval before paid actions**.

## Honest scope

This is an independent technical lab, not a product of VibeMarketolog and not a claim of affiliation. The knowledge base is built only from its public Agent API documentation. The application does not issue a paid generation until an operator reviews a free `/generate/estimate` result and explicitly confirms it.

## Components

| Component | Evidence of skill |
|---|---|
| `rag/` | document fetch, chunking, OpenAI `text-embedding-3-small`, persistent local Chroma, source citations |
| `rag/evaluation/` | ground-truth retrieval set, hit@k and MRR metrics |
| `backend/` | FastAPI, SQLite audit trail, Vibe API adapter, HMAC webhook validation, explicit cost approval |
| `frontend/` | React/Vite internal UI for search, estimate, confirmation and feedback |
| `n8n/` | importable scheduled health-and-digest workflow, Telegram delivery |
| `dify/` | Dify Cloud instructions, citation-first system prompt and acceptance checks |
| `deploy/` | Docker Compose, nginx templates, resource limits and operational runbook |

## Security controls

- Secrets are server-only in `/opt/vibe-content-lab/.env`, never in Git or browser JavaScript.
- The backend calls `/generate/estimate` first. `POST /generations/confirm` needs the returned one-time estimate ID.
- The Vibe API key should have only `read` and `generate` scopes, a small `daily_spend_limit`, and an IP allowlist for the server.
- Incoming generation webhooks are validated with `X-Vibe-Signature` and a constant-time HMAC comparison.
- `n8n.lab.syntog.ru` is a private operator interface behind nginx Basic Auth.
- The Dify component uses the separate private Dify Cloud workspace, rather than copying
  Factory credentials or trying to run Dify below its vendor memory minimum.

## Setup

1. Create `/opt/vibe-content-lab/.env` on the server using `.env.example`, then `chmod 600` it.
2. Set a separate OpenAI project key and a Vibe API key. Do not reuse Factory credentials.
3. Start with `docker compose --env-file /opt/vibe-content-lab/.env up -d --build`.
4. Build the knowledge index: `docker compose exec api python -m rag.ingest`.
5. Run retrieval evaluation: `docker compose exec api python -m rag.evaluation.run`.

The deploy and workflow steps are intentionally not claimed as completed until they have real execution records.