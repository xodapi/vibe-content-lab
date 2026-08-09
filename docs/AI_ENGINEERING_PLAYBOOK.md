# AI engineering delivery playbook

This playbook is a reusable standard for internal AI tools. It deliberately separates
**a prototype that answers once** from **a system that colleagues can use repeatedly**.

## 1. Discovery: define the decision, not the model

Before choosing a framework, write one page:

- user, business decision and current manual process;
- input classes, including confidential or personal data;
- permitted actions and actions that require a human;
- measurable outcome, baseline and error cost;
- non-goals, owner and rollback path.

**Exit gate:** a business owner can identify a useful answer and an unacceptable answer
without referring to a model.

## 2. Data contract and retrieval

For each source, record:

- owner, public/internal classification, update cadence and retention;
- ingestion time, document version/hash and access boundary;
- parsing/OCR quality and known gaps;
- chunking rule, embedding model, top-K and reranking choice.

The application must show the source fragment with each material factual answer. A
retrieval miss is an expected result, not permission to invent an answer.

**Exit gate:** a held-out question set covers normal, ambiguous, stale and
out-of-scope questions.

## 3. Evaluation before release

Maintain versioned cases in Git, each with:

```json
{
  "id": "scope-missing",
  "question": "What happens with a missing scope?",
  "expected_evidence": ["403", "insufficient_scope"],
  "risk": "high",
  "expected_behavior": "cite source or explicitly abstain"
}
```

Measure three layers, not one vanity score:

| Layer | Minimum signal |
|---|---|
| Retrieval | Hit@K, MRR, source freshness, retrieval miss rate |
| Answer | faithfulness/citation correctness, task completion, abstention correctness |
| System | latency, error rate, cost per successful task, human override rate |

Use automated metrics to detect regressions, then sample high-risk outputs for human
review. An LLM judge is a useful secondary signal, not the sole acceptance authority.

**Exit gate:** baseline metrics and explicit release thresholds are recorded.

## 4. Human control and security

Use a capability table:

| Action class | Default | Example |
|---|---|---|
| Read public docs | automatic | search and cite |
| Read internal docs | least privilege | knowledge-base query |
| Spend money | estimate then explicit confirmation | content generation |
| Mutate CRM/ERP | explicit human approval | create deal, payment, order |
| External publish/send | draft plus approval | publish campaign, email client |

Never put provider tokens in a browser, prompt, workflow export or Git history. Use
short-lived/limited credentials where available, IP restrictions, scope minimisation,
spend caps, HMAC verification for webhooks and idempotency keys for retried writes.

**Exit gate:** an attack or misuse path has a documented prevention/detection/response
control.

## 5. Software delivery standards

These are implementation-independent practices, not framework badges:

- **12-factor configuration:** configuration and secrets outside source control;
- **contract first:** typed request/response schemas; version APIs intentionally;
- **reproducible environment:** pinned dependencies, Docker build, `.env.example`;
- **automated gate:** formatter/linter, unit tests, JSON/schema validation, UI build;
- **small reversible releases:** feature flag or approval gate, rollback procedure;
- **observability:** structured logs with correlation IDs, latency, error, cost,
  retrieval and approval events;
- **operational ownership:** runbook, alert condition, data-retention decision and
  named owner.

For this repository these practices are executable through:

```powershell
.\scripts\harness.ps1 check
.\scripts\harness.ps1 test
```

## 6. Definition of done for an AI workflow

A workflow is done only when all apply:

- [ ] it answers a real user task against an agreed baseline;
- [ ] input/source permissions and retention are known;
- [ ] eval cases, results and release threshold exist;
- [ ] failure, abstention and human approval behaviour are testable;
- [ ] secrets are external, actions are idempotent where relevant;
- [ ] logs support incident reconstruction without exposing sensitive content;
- [ ] a non-engineer has a short instruction and escalation route;
- [ ] deployment and rollback have been rehearsed once.
