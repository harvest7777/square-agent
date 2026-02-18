# Square Coffee Ordering Agent

A conversational coffee ordering agent built for the **Fetch.ai Coffee x On Call** event. Customers interact with the agent through AgentVerse to browse the menu, build an order, and place it — all powered by natural language.

Built with [Fetch.ai uAgents](https://fetch.ai/docs/concepts/agents/agents), [LangGraph](https://langchain-ai.github.io/langgraph/), [Google Gemini](https://ai.google.dev/), and the [Square API](https://developer.squareup.com/).

## Setup

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

See `.env.example` for descriptions of each variable.

If you're using Supabase (see `services/supabase_client.py`), you must also set:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Docker

```bash
docker compose up --build
```

## Local Development

```bash
pip install -r requirements.txt
python -m wrapped_uagent.agent
```
