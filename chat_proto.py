from datetime import datetime
from uuid import uuid4

from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from menu import MENU_ITEMS, get_menu
from square_utils import place_order
from uagents_utils import Intent, classify_intent, get_message_history, get_requested_menu_item_number, mark_user_as_ordered, user_has_ordered

chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    ctx.logger.info("Received msg")
    await ctx.send(sender,ChatMessage(content=[TextContent("Hardcoded")]))


# This is needed to be compliant with AgentVerse's chat protocol
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    user_id = sender
    messages = get_message_history(chat_id="TODO")

    # Storing messages
    # TODO: use the get_message_history and append_message_to_history here

    # Order flow
    intent: Intent = classify_intent(chat_history=messages)

    match (intent):
        case Intent.PLACE_ORDER:
            if user_has_ordered(ctx=ctx, user_id=user_id):
                ctx.send(sender, ChatMessage(content="Sorry! Only one per person for promotional event"))
            else:
                menu_item_number = get_requested_menu_item_number(chat_history=messages)
                variant_id = MENU_ITEMS[menu_item_number]
                place_order(variant_id=variant_id, idempotency_key=uuid4())
                mark_user_as_ordered(user_id=user_id)
        case Intent.WANT_TO_ORDER:
            menu = get_menu()
            msg = "Thanks for coming to the promotional Fetch-A-Coffee event! Please select something from the menu below\n" + menu
            ctx.send(sender, ChatMessage(content=msg))
        case _:
            ctx.send(sender, ChatMessage(content="Sorry, I can only help you order a coffee. Try choosing something from the menu or ask me for the menu!"))
            
