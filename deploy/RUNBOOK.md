# Deployment runbook

This is a checklist for the server phase. Do not run it until the separate
`/opt/vibe-content-lab/.env` has been created and checked.

## Server preparation

```bash
sudo mkdir -p /opt/vibe-content-lab
sudo chown "$USER":"$USER" /opt/vibe-content-lab
git clone <private-repository-url> /opt/vibe-content-lab
cp /opt/vibe-content-lab/.env.example /opt/vibe-content-lab/.env
chmod 600 /opt/vibe-content-lab/.env
```

Set separate values for `OPENAI_API_KEY`, `VIBE_API_TOKEN`, and
`VIBE_WEBHOOK_SECRET`. Use a Vibe key with only the scopes required for the demo,
small `daily_spend_limit`, and an IP allowlist. Never print `.env` to logs.

## Start and verify

```bash
cd /opt/vibe-content-lab
docker compose --env-file .env up -d --build
docker compose ps
curl -fsS http://127.0.0.1:18080/health
docker compose exec api python -m rag.ingest
docker compose exec api python -m rag.evaluation.run
```

The first index build calls OpenAI embeddings. The evaluation is retrieval-only and
does not spend VibeMarketolog credits.

## Nginx and TLS

1. Create a Basic Auth file outside Git:

   ```bash
   sudo htpasswd -c /etc/nginx/.htpasswd-vibe-lab sergey
   ```

2. Install `deploy/nginx-lab.syntog.ru.conf.example` as the site config.
3. Confirm DNS points `lab.syntog.ru` to the server.
4. Obtain a certificate with certbot, then run `nginx -t` and reload nginx.
5. Verify `/health`, the UI, and the RAG query through HTTPS.

Keep the lab behind Basic Auth. If a future Vibe webhook is enabled, add a narrowly
scoped unauthenticated location only after validating its HMAC signature in FastAPI.
