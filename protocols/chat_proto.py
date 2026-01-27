from datetime import datetime
from uuid import uuid4

from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from core.menu import MENU_ITEMS, get_menu
from services.square_utils import place_order
from core.intent import Intent
from utils.uagents_utils import classify_intent, get_message_history, get_requested_menu_item_number, mark_user_as_ordered, user_has_ordered, append_message_to_history

chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    ctx.logger.info("Received msg")

    # Store incoming user message
    for item in msg.content:
        if isinstance(item, TextContent):
            append_message_to_history(ctx=ctx, chat_id=sender, message=item.text)
            ctx.logger.info(f"Stored message from {sender}: {item.text}")


# This is needed to be compliant with AgentVerse's chat protocol
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    user_id = sender

    # Retrieve message history for this user
    messages = get_message_history(ctx=ctx, chat_id=user_id)
    ctx.logger.info(f"Retrieved {len(messages)} messages for user {user_id}")

    # Order flow
    intent: Intent = classify_intent(chat_history=messages)

    match (intent):
        case Intent.PLACE_ORDER:
            if user_has_ordered(ctx=ctx, user_id=user_id):
                await ctx.send(sender, ChatMessage(content=[TextContent(text="Sorry! Only one per person for promotional event")]))
            else:
                menu_item_number = get_requested_menu_item_number(chat_history=messages)
                variation_id = MENU_ITEMS[menu_item_number]
                place_order(variation_id=variation_id, idempotency_key=str(uuid4()))
                mark_user_as_ordered(ctx=ctx, user_id=user_id)
                await ctx.send(sender, ChatMessage(content=[TextContent(text="Your order has been placed! Thank you!")]))
        case Intent.WANT_TO_ORDER:
            menu = get_menu()
            msg = "Thanks for coming to the promotional Fetch-A-Coffee event! Please select something from the menu below\n" + menu
            await ctx.send(sender, ChatMessage(content=[TextContent(text=msg)]))
        case _:
            await ctx.send(sender, ChatMessage(content=[TextContent(text="Sorry, I can only help you order a coffee. Try choosing something from the menu or ask me for the menu!")]))
