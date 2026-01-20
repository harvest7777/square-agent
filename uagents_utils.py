from enum import Enum
from uagents import Context
import re


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


def classify_intent(chat_history: list) -> Intent:
    """
    Classify the user's intent from the chat history.

    This function analyzes the chat history (most recent messages first) to determine
    the user's intent using keyword matching patterns.

    Args:
        chat_history: List of message strings from the chat

    Returns:
        Intent enum value indicating the user's intent:
        - Intent.WANT_TO_ORDER: User expresses interest in ordering (e.g., asking to see menu,
          browsing items, but not yet ready to place an order)
        - Intent.PLACE_ORDER: User wants to actually place/complete an order (e.g., confirming
          selection, requesting order completion)
        - Intent.UNKNOWN: Fallback when intent cannot be determined from chat history
    """
    if not chat_history:
        return Intent.UNKNOWN

    # Keywords that indicate user wants to PLACE a specific order (needs item reference)
    place_order_keywords = [
        "take", "have", "get", "order", "buy", "purchase", "give", "want"
    ]

    # Item reference indicators (numbers or ordinals)
    item_indicators = [
        "1", "2", "3", "#1", "#2", "#3",
        "one", "two", "three",
        "first", "second", "third",
        "1st", "2nd", "3rd",
        "item", "number", "option"
    ]

    # Keywords that indicate user wants to SEE the menu or browse
    want_to_order_keywords = [
        "menu", "options", "choices", "available", "offer", "list",
        "show", "see", "view", "browse", "display",
        "what", "which", "any",
        "help", "assist", "recommend", "suggestion",
        "coffee", "drink", "drinks", "beverage"
    ]

    # Process messages from most recent to oldest
    for message in reversed(chat_history):
        message_lower = message.lower().strip()

        # Check for PLACE_ORDER: needs both an action keyword AND an item indicator
        has_action = any(keyword in message_lower for keyword in place_order_keywords)
        has_item = any(indicator in message_lower for indicator in item_indicators)

        if has_action and has_item:
            return Intent.PLACE_ORDER

        # Check for WANT_TO_ORDER: just needs browsing/menu keywords
        if any(keyword in message_lower for keyword in want_to_order_keywords):
            return Intent.WANT_TO_ORDER

    return Intent.UNKNOWN

def get_requested_menu_item_number(chat_history: list) -> int:
    """
    Extract the menu item number that the user requested from the chat history.

    This function parses through the chat history (most recent first) and looks for
    menu item numbers using pattern matching. It supports various formats:
    - Direct numbers: "1", "2", "3"
    - Item references: "item 1", "number 2", "#3"
    - Ordinal words: "first", "second", "third"

    Args:
        chat_history: List of message strings from the chat

    Returns:
        The menu item number (integer) that the user requested

    Raises:
        ValueError: If unable to determine what menu item the user was trying to order
    """

    # Maybe we can do llama index for this
    # Word to number mapping for ordinal references
    word_to_number = {
        "first": 1, "one": 1, "1st": 1,
        "second": 2, "two": 2, "2nd": 2,
        "third": 3, "three": 3, "3rd": 3,
    }

    # Valid menu item numbers (1, 2, 3 based on MENU_ITEMS)
    valid_items = {1, 2, 3}

    # Process messages from most recent to oldest
    for message in reversed(chat_history):
        message_lower = message.lower()

        # Check for ordinal words first
        for word, number in word_to_number.items():
            if word in message_lower:
                return number

        # Pattern to match item references like "item 1", "number 2", "#3", or standalone digits
        patterns = [
            r'item\s*(\d+)',      # "item 1", "item1"
            r'number\s*(\d+)',    # "number 2", "number2"
            r'#(\d+)',            # "#3"
            r'option\s*(\d+)',    # "option 1"
            r'\b(\d+)\b',         # standalone digit
        ]

        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                item_number = int(match.group(1))
                if item_number in valid_items:
                    return item_number

    raise ValueError("Unable to determine the requested menu item from chat history")

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