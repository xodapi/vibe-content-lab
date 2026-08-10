# Публичные доказательства квалификации

Репозиторий: [github.com/xodapi/vibe-content-lab](https://github.com/xodapi/vibe-content-lab)

Live demo: [lab.syntog.ru](https://lab.syntog.ru)  
Operator UI: `n8n.lab.syntog.ru` (закрыт Basic Auth)

## Матрица доказательств

| Компетенция | Где проверять | Что доказано |
|---|---|---|
| RAG и embeddings | [`rag/`](../rag/) | Загрузка публичного источника, очистка, heading-aware chunking, embeddings и Chroma retrieval |
| Retrieval evaluation | [`rag/evaluation/`](../rag/evaluation/) | Versioned ground-truth cases, Hit@4 и MRR@4 |
| Backend engineering | [`backend/`](../backend/) | FastAPI, typed contracts, SQLite audit trail, explicit errors |
| AI safety | [`backend/app/main.py`](../backend/app/main.py) | Estimate → explicit confirmation → generation, spend guard и feedback |
| API integration | [`backend/app/vibe_client.py`](../backend/app/vibe_client.py) | Bearer auth, idempotency, HMAC verification и timeout/error handling |
| Frontend | [`frontend/src/main.jsx`](../frontend/src/main.jsx) | Интерфейс с цитатами, сметой и контролируемым действием |
| Low-code automation | [`n8n/`](../n8n/) и [`dify/`](../dify/) | Importable n8n workflow и Dify Cloud workflow specification |
| Delivery discipline | [`.github/workflows/verify.yml`](../.github/workflows/verify.yml) | CI: tests, Ruff, compile, JSON checks и React build |
| Operational deployment | [`docker-compose.yml`](../docker-compose.yml), [`deploy/`](../deploy/) | Loopback-only ports, nginx reverse proxy, TLS, Basic Auth и runbook |
| Engineering judgment | [`AI_ENGINEERING_PLAYBOOK.md`](AI_ENGINEERING_PLAYBOOK.md) | Discovery, data contract, evaluation gates, rollback и Definition of Done |
| Research literacy | [`RESEARCH_AND_STANDARDS.md`](RESEARCH_AND_STANDARDS.md) | RAGAS, CRAG, RAGChecker, NIST AI RMF и OWASP LLM guidance |

## Уже проверено

- локальный harness: **3 tests passed**;
- Ruff: passed;
- Python compilation: passed;
- JSON validation: passed;
- React production build: passed;
- DNS для обоих поддоменов указывает на сервер;
- live endpoints требуют Basic Auth;
- TLS-сертификат покрывает оба домена;
- application ports доступны только на loopback;
- provider keys намеренно не добавлены.

## Что нельзя заявлять до фактического запуска

Не следует выдавать за доказанные факты без execution evidence:

- качество на реальных рабочих вопросах;
- latency, uptime и production SLA;
- экономический эффект;
- успешный Dify Cloud execution;
- успешный n8n Telegram execution;
- безопасность корпоративных документов.

Скриншоты и логи из Dify/n8n добавляются только после реального запуска и должны
быть очищены от токенов, chat ID, личных данных и содержимого приватных переписок.

## Рекомендуемая формулировка для резюме

> Built and deployed an evidence-driven AI engineering lab with RAG over public API
> documentation, Chroma vector search, retrieval evaluation, FastAPI/React, n8n and
> Dify Cloud workflow specifications. Added CI, Docker, nginx/TLS, Basic Auth,
> server-side secrets, HMAC webhooks, idempotency and explicit human approval before
> paid generation.
