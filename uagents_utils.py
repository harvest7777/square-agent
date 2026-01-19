from enum import Enum
from uagents import Context


class Intent(str, Enum):
    """Intent enum for user actions."""
    WANT_TO_ORDER = "want to order"
    PLACE_ORDER = "place order"
    UNKNOWN = "unknown"  # Fallback when intent cannot be determined

def _get_user_orderd_key(user_id: str) -> str:
    return f"ordered-{user_id}"

def _get_message_history_key(chat_id: str) -> str:
    return f"message-history-{chat_id}"

def mark_user_as_ordered(ctx: Context, user_id: str) -> None:
    ctx.storage.set(_get_user_orderd_key(user_id), True)

def user_has_ordered(ctx: Context, user_id: str) -> bool: 
    return ctx.storage.get(_get_user_orderd_key(user_id))


# TODO
def classify_intent(chat_history: any) -> Intent:
    """
    TODO: Classify the user's intent from the chat history.
    
    This function is a placeholder and needs to be implemented. We don't know how
    the developer API will work yet. Developers should look into the implementation
    and get back to the team with their findings.
    
    If the intent cannot be determined from the chat history, this function should
    return Intent.UNKNOWN as a fallback.
    
    Args:
        chat_history: The chat history containing user messages (format TBD)
    
    Returns:
        Intent enum value indicating the user's intent:
        - Intent.WANT_TO_ORDER: User expresses interest in ordering (e.g., asking to see menu, 
          browsing items, but not yet ready to place an order)
        - Intent.PLACE_ORDER: User wants to actually place/complete an order (e.g., confirming 
          selection, requesting order completion)
        - Intent.UNKNOWN: Fallback when intent cannot be determined from chat history
    
    Note:
        This is a TODO item. Implementation details need to be researched and discussed with the team.
    """
    pass

# TODO
def get_requested_menu_item_number(chat_history: any) -> int:
    """
    TODO: Extract the menu item number that the user requested from the chat history.
    
    This function is a placeholder and needs to be implemented. We don't know how
    the developer API will work yet. Developers should look into the implementation
    and get back to the team with their findings.
    
    This function will raise an error if it is unable to determine what the user
    was trying to order from the chat history.
    
    Args:
        chat_history: The chat history containing user messages (format TBD)
    
    Returns:
        The menu item number (integer) that the user requested
    
    Raises:
        ValueError: If unable to determine what menu item the user was trying to order
    
    Note:
        This is a TODO item. Implementation details need to be researched and discussed with the team.
    """
    pass

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