from uagents import Context

def _get_user_orderd_key(user_id: str) -> str:
    return f"ordered-{user_id}"

def _get_message_history_key(chat_id: str) -> str:
    return f"message-history-{chat_id}"

def mark_user_as_ordered(ctx: Context, user_id: str) -> None:
    ctx.storage.set(_get_user_orderd_key(user_id), True)

def user_has_ordered(ctx: Context, user_id: str) -> bool: 
    return ctx.storage.get(_get_user_orderd_key(user_id))

def get_message_history(ctx: Context, chat_id: str) -> list:
    """
    Retrieve the message history for a particular chat ID.

    Args:
        ctx: The uagents Context for accessing storage
        chat_id: The unique identifier for the chat whose message history should be retrieved

    Returns:
        List of messages for the specified chat ID, or empty list if no history exists
    """
    history = ctx.storage.get(_get_message_history_key(chat_id))
    return history if history is not None else []

def append_message_to_history(ctx: Context, chat_id: str, message: str) -> None:
    """
    Append a message to the message history for a particular chat ID.

    Args:
        ctx: The uagents Context for accessing storage
        chat_id: The unique identifier for the chat to append the message to
        message: The message content to append to the chat history

    Returns:
        None
    """
    history = get_message_history(ctx, chat_id)
    history.append(message)
    ctx.storage.set(_get_message_history_key(chat_id), history)