# n8n workflow preparation

`daily-api-knowledge-digest.json` is an inactive workflow export. It runs on weekdays
at 09:00 Moscow time:

```text
Schedule → Lab RAG HTTP endpoint → message formatting → Telegram
```

## Manual activation

1. Import the JSON in n8n.
2. Add a **Telegram** credential in the Telegram node. The bot token belongs in n8n
   credentials, not the repository or the exported workflow.
3. Keep the HTTP Request node on the internal Docker URL:

   `http://api:8000/api/knowledge/answer`

   This avoids sending the request through the public nginx Basic Auth boundary.
   The URL works because the `api` and `n8n` services share the Compose network.
4. Set `TELEGRAM_CHAT_ID` in the server `.env`. Do not store a bot token or personal
   chat identifier in the workflow export.
5. Run it once manually. Confirm the output and retain a screenshot of the green
   execution.
6. Only then activate the schedule.

## Evidence

Keep the following only after real execution:

- `evidence/n8n-canvas.png`;
- `evidence/n8n-successful-execution.png`;
- Telegram message screenshot, with personal chat identifiers blurred.
