# Why this Lab uses evaluation, citations and human approval

This document distinguishes **research evidence**, **industry security guidance** and
**engineering practice**. It does not claim that one paper proves a product feature.

## Research evidence

### RAG is a pipeline, therefore evaluate retrieval and answer generation separately

- **RAGAS**, Es et al., EACL 2024, introduced reference-free metrics for RAG pipelines,
  including context relevance, answer relevance and faithfulness.
  [Paper](https://aclanthology.org/2024.eacl-demo.16/)
- **CRAG**, Yang et al., NeurIPS 2024, provides a benchmark explicitly designed to
  expose the limits of evaluating only idealized RAG questions.
  [Paper](https://proceedings.neurips.cc/paper_files/paper/2024/hash/1435d2d0fca85a84d8d35a2dd7d3a1-Abstract-Conference.html)
- **RAGChecker**, Ru et al., 2024, proposes fine-grained diagnostics across
  retriever and generator components rather than a single end-to-end score.
  [Paper](https://arxiv.org/abs/2408.08067)
- **Evaluation of Retrieval-Augmented Generation: A Survey**, Gao et al., 2024,
  catalogues the separation of retrieval, generation and end-to-end evaluation.
  [Paper](https://arxiv.org/abs/2405.07437)

**Lab application:** `rag/evaluation/ground_truth.json` uses named test cases and
reports Hit@4 plus MRR@4. This is an intentionally small smoke suite, not a claim of a
production benchmark. Before release, it needs representative user tasks and human
review of citation correctness.

### Human approval is a safety boundary, not a UX detail

- **Greshake et al.**, *Not what you've signed up for*, 2023, demonstrated indirect
  prompt injection risks in LLM-integrated applications.
  [Paper](https://arxiv.org/abs/2302.12173)
- The **NIST AI RMF: Generative AI Profile** (NIST AI 600-1, 2024) frames AI risk
  management through Govern, Map, Measure and Manage functions.
  [Official publication](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- **OWASP Top 10 for LLM Applications 2025** lists prompt injection (LLM01) and
  excessive agency (LLM06) among principal application risks.
  [Official project](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

**Lab application:** real generation requires `estimate → operator confirmation →
generate`; the server, not browser JavaScript, holds provider keys; webhook payloads
require an HMAC signature.

## Industry standards used as design references

| Practice | Applied here |
|---|---|
| NIST AI RMF | risk/control record, evaluation, human action boundaries |
| OWASP LLM guidance | untrusted context awareness, least privilege, approval for effects |
| OpenAPI/contract-first API design | typed FastAPI payloads and explicit errors |
| SRE/observability practice | health endpoint, deploy runbook, audit records to extend with traces |
| 12-factor configuration | secret-free repo and environment-based configuration |

## What still requires evidence after deployment

These cannot be claimed until actual use:

- response latency and uptime;
- retrieval quality on representative staff questions;
- value versus a human baseline;
- successful Dify/n8n executions;
- behavior under stale documents, malformed files and provider outages.
