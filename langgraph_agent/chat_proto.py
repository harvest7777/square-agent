from datetime import datetime

from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
from langchain_core.runnables import RunnableConfig

from graph.graph import graph
from graph.checkpointer import setup_checkpointer

# Initialize checkpoint tables on module load
setup_checkpointer()

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle incoming chat messages by routing them through the langgraph flow.

    Uses the sender address as the thread_id so each user has their own
    persistent conversation state (cart, etc.).
    """
    ctx.logger.info(f"Received message from {sender}")

    # Extract text content from the message
    user_input = ""
    for item in msg.content:
        if isinstance(item, TextContent):
            user_input = item.text
            break

    if not user_input:
        await ctx.send(
            sender,
            ChatMessage(content=[TextContent(text="I didn't receive any text. Please try again.")])
        )
        return

    ctx.logger.info(f"User input: {user_input}")

    # Use session as thread_id for conversation persistence
    thread_id = str(ctx.session)
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    try:
        # Invoke the langgraph flow
        result = graph.invoke(
            {"user_input": user_input},
            config
        )

        # Extract bot response
        bot_response = result.get("bot_response", "")
        if not bot_response:
            bot_response = "I'm sorry, I couldn't process your request."

        ctx.logger.info(f"Bot response: {bot_response}")

    except Exception as e:
        ctx.logger.error(f"Error processing message: {e}")
        bot_response = "Sorry, something went wrong. Please try again."

    # Send response back to user
    await ctx.send(
        sender,
        ChatMessage(content=[TextContent(text=bot_response)])
    )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgement messages (required for AgentVerse chat protocol compliance)."""
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
