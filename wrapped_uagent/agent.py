"""
LangGraph Agent - A uAgent that hosts the langgraph ordering flow.

This agent exposes the langgraph-based food ordering bot via the Fetch.ai
chat protocol, making it accessible through AgentVerse.

Usage:
    python -m langgraph_agent.agent
"""

import os
import atexit

from uagents import Agent
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv

from langgraph_agent.chat_proto import chat_proto
from graph.checkpointer import cleanup_checkpointer

load_dotenv()

# Create the agent
agent = Agent(
    name="langgraph-ordering-agent",
    seed=os.getenv("LANGGRAPH_AGENT_SEED", os.getenv("AGENT_SEED")),
    port=8001,  # Different port from main agent
    mailbox=True,
)

# Fund the agent wallet if needed
fund_agent_if_low(str(agent.wallet.address()))

# Include the chat protocol
agent.include(chat_proto, publish_manifest=True)

# Cleanup checkpointer on exit
atexit.register(cleanup_checkpointer)


@agent.on_event("startup")
async def on_startup(ctx):
    ctx.logger.info(f"LangGraph Agent started!")
    ctx.logger.info(f"Agent address: {agent.address}")
    ctx.logger.info(f"Agent wallet: {agent.wallet.address()}")


if __name__ == "__main__":
    agent.run()
