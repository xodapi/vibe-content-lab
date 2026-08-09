# Dify acceptance checks

Run these manually after indexing. Record **pass / partial / fail**, the cited source
title, and a screenshot in `evidence/evaluation.md`.

| ID | Question | Expected facts |
|---|---|---|
| D01 | Какой заголовок авторизации нужен для Agent API? | `Authorization: Bearer` |
| D02 | Как получить смету до списания? | `POST /generate/estimate`, no charge |
| D03 | Как предотвратить несовместимые поля до списания? | `strict=true` |
| D04 | Как безопасно повторить генерацию после timeout? | same idempotency key, duplicate semantics |
| D05 | Как проверяется webhook callback? | HMAC SHA-256 / signature |
| D06 | Как узнать результат видео-генерации? | status endpoint / polling; signed display URL |
| D07 | Что будет при отсутствии scope? | 403 `insufficient_scope`, granted/required |
| D08 | Можно ли получить список актуальных параметров модели? | `/capabilities` |

## Acceptance gate

- D01–D08 must have a cited response.
- At least 7/8 must be `pass`.
- Every answer outside retrieved evidence must explicitly state that documentation is
  insufficient, rather than inventing an answer.
- Retry the failed case after correcting chunking or Top K. Retain both the original
  failure and the rerun in the log.
