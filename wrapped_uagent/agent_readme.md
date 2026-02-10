# LangGraph Ordering Agent

A Fetch.ai **uAgent** that exposes a LangGraph-based food ordering flow over the Fetch.ai chat protocol, making it usable from **AgentVerse** and other chat clients.

---

## Purpose

This agent provides a conversational interface for ordering from a Square-backed catalog. Users can view the menu, add items to a cart, review the cart, confirm or cancel orders, and get help—all via natural-language chat. Each user session maintains its own conversation state (e.g., cart) through a persistent LangGraph thread.

---

## Functionalities

- **Chat protocol** — Implements the Fetch.ai chat protocol (`ChatMessage`, `ChatAcknowledgement`) so the agent can be discovered and messaged from AgentVerse and compatible clients.
- **Intent-based flow** — Incoming messages are classified by intent and routed to the appropriate handler:
  - **Show menu** — Returns the current catalog (from Square), formatted as a numbered menu.
  - **Add to cart** — Parses item selection (e.g., “I’ll take item 2”) and adds the corresponding Square variation to the session cart.
  - **Show cart** — Lists current cart contents and optional summary.
  - **Confirm order** — Places the order with Square using the current cart and clears the cart on success.
  - **Cancel order** — Clears the cart without placing an order.
  - **Show help** — Returns guidance on what the user can say.
  - **Handle unknown** — Fallback when intent cannot be determined; can prompt for clarification or suggest help.
- **Session persistence** — Uses the chat session (e.g., `ctx.session`) as the LangGraph `thread_id`, so each user has isolated, stateful conversations (cart and flow state).
- **Square integration** — Catalog and order placement are backed by the Square API (via `SquareClient`); the agent uses a merchant bearer token and optional catalog allowlist/configuration from the `graph` module.
- **Startup and lifecycle** — Logs agent address and wallet on startup; registers checkpointer cleanup on process exit.

---

## Usage Guidelines

- **Running the agent**  
  From the project root:

  ```bash
  python -m wrapped_uagent.agent
  ```

  (Or run the `agent` module inside `wrapped_uagent` with the same environment.)

- **Environment**  
  Ensure required env vars are set (e.g. `BEARER_TOKEN`, `ENVIRONMENT` for Square; `LANGGRAPH_AGENT_SEED` or `AGENT_SEED` for the uAgent). The agent uses port **8001** and expects a mailbox to be configured for the chat protocol.

- **Chat clients**  
  Use a client that supports the Fetch.ai chat protocol (e.g. AgentVerse). Send text messages to the agent; it will reply with a single text response per turn. Mentions (e.g. `@agent...`) in the message body are stripped before processing.

- **Conversation design**  
  For best results, users should use clear intents (e.g. “show menu”, “add item 2”, “confirm order”). The agent is intended for short, turn-by-turn interactions rather than long multi-step reasoning in a single message.

---

## Licensing Details

See the project root for license information. This agent is part of the broader Square ordering/LangGraph integration and is subject to the same license as the repository.

---

## Contact Information

For issues or contributions related to this agent, use the project’s standard contact or issue tracker (e.g. repository issues or maintainer contact listed in the root README).

---

## Acknowledgments

- **Fetch.ai** — uAgents framework and chat protocol.
- **LangGraph** — Conversation and ordering workflow (state graph, checkpointer).
- **Square** — Catalog and order APIs backing the menu and order placement.
