from uagents import Context

from core.intent import Intent
from core.intent_examples import SIMILARITY_THRESHOLD, MENU_ITEM_SIMILARITY_THRESHOLD
from services.embedding_utils import get_embedding, cosine_similarity, get_intent_embeddings, get_menu_item_embeddings


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
    Classify the user's intent from the chat history using semantic search.

    This function uses OpenAI embeddings to semantically match the user's message
    against example phrases for each intent. The workflow:
    1. Get the user's latest message
    2. Convert it to an embedding
    3. For each intent, compare user embedding to each example and take best score
    4. Pick the intent with the highest score
    5. If score < threshold -> UNKNOWN

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

    # Get the most recent message from the user
    latest_message = chat_history[-1].strip()

    if not latest_message:
        return Intent.UNKNOWN

    try:
        # Get embedding for the user's message
        user_embedding = get_embedding(latest_message)

        # Get cached embeddings for intent examples
        intent_embeddings = get_intent_embeddings()

        # Calculate best similarity score for each intent
        intent_scores = {}

        for intent_name, example_embeddings in intent_embeddings.items():
            # Find the highest similarity score among all examples for this intent
            best_score = max(
                cosine_similarity(user_embedding, example_emb)
                for example_emb in example_embeddings
            )
            intent_scores[intent_name] = best_score

        # Find the intent with the highest score
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]

        # If best score is below threshold, return UNKNOWN
        if best_score < SIMILARITY_THRESHOLD:
            return Intent.UNKNOWN

        # Map intent name to Intent enum
        intent_mapping = {
            "PLACE_ORDER": Intent.PLACE_ORDER,
            "WANT_TO_ORDER": Intent.WANT_TO_ORDER,
        }

        return intent_mapping.get(best_intent, Intent.UNKNOWN)

    except Exception as e:
        # If embedding fails (API error, etc.), fall back to UNKNOWN
        print(f"Error in classify_intent: {e}")
        return Intent.UNKNOWN


def get_requested_menu_item_number(chat_history: list) -> int:
    """
    Extract the menu item number that the user requested from the chat history using semantic search.

    This function uses OpenAI embeddings to semantically match the user's message
    against example phrases for each menu item. The workflow:
    1. Get the user's latest message
    2. Convert it to an embedding
    3. For each menu item, compare user embedding to each example and take best score
    4. Pick the menu item with the highest score
    5. If score < threshold -> raise ValueError

    Args:
        chat_history: List of message strings from the chat

    Returns:
        The menu item number (integer) that the user requested

    Raises:
        ValueError: If unable to determine what menu item the user was trying to order
    """
    if not chat_history:
        raise ValueError("Unable to determine the requested menu item from chat history")

    # Get the most recent message from the user
    latest_message = chat_history[-1].strip()

    if not latest_message:
        raise ValueError("Unable to determine the requested menu item from chat history")

    try:
        # Get embedding for the user's message
        user_embedding = get_embedding(latest_message)

        # Get cached embeddings for menu item examples
        menu_item_embeddings = get_menu_item_embeddings()

        # Calculate best similarity score for each menu item
        item_scores = {}

        for item_number, example_embeddings in menu_item_embeddings.items():
            # Find the highest similarity score among all examples for this item
            best_score = max(
                cosine_similarity(user_embedding, example_emb)
                for example_emb in example_embeddings
            )
            item_scores[item_number] = best_score

        # Find the menu item with the highest score
        best_item = max(item_scores, key=item_scores.get)
        best_score = item_scores[best_item]

        # If best score is below threshold, raise error
        if best_score < MENU_ITEM_SIMILARITY_THRESHOLD:
            raise ValueError("Unable to determine the requested menu item from chat history")

        return best_item

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        # If embedding fails (API error, etc.), raise ValueError
        print(f"Error in get_requested_menu_item_number: {e}")
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
