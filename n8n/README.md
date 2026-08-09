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
3. In the HTTP Request node use the production URL once deployed:

   `https://lab.syntog.ru/api/knowledge/answer`

   The development hostname `http://api:8000/...` works only when n8n and API share a
   Docker network.
4. Set `TELEGRAM_CHAT_ID` in n8n’s runtime environment or replace the expression with
   the chat ID in the node. Do not store the bot token in a workflow field.
5. Run it once manually. Confirm the output and retain a screenshot of the green
   execution.
6. Only then activate the schedule.

## Evidence

Keep the following only after real execution:

- `evidence/n8n-canvas.png`;
- `evidence/n8n-successful-execution.png`;
- Telegram message screenshot, with personal chat identifiers blurred.
