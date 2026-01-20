from enum import Enum
from uagents import Context
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client - API key will be loaded from environment
# Set OPENAI_API_KEY in your .env file
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding model to use
EMBEDDING_MODEL = "text-embedding-3-small"

# Example phrases for each intent (used for semantic matching)
INTENT_EXAMPLES = {
    "PLACE_ORDER": [
        "I'll take item 1",
        "Give me the second one",
        "I want number 2",
        "Order the first item please",
        "Can I get item 3",
        "I'd like to have the third option",
        "Let me get number one",
        "I'll have the second drink",
        "Put in an order for item 2",
        "I want to buy the first one",
    ],
    "WANT_TO_ORDER": [
        "Show me the menu",
        "What do you have",
        "What's available",
        "I want to order something",
        "What are my options",
        "Can I see what you offer",
        "What drinks do you have",
        "Help me order",
        "I'm interested in ordering",
        "What can I get here",
    ],
}

# Similarity threshold - below this returns UNKNOWN
SIMILARITY_THRESHOLD = 0.3

# Cache for intent example embeddings (computed once)
_intent_embeddings_cache = {}

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


def _get_embedding(text: str) -> list:
    """
    Get the embedding vector for a text string using OpenAI's embedding model.

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    text = text.replace("\n", " ").strip()
    response = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def _cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score between -1 and 1
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def _get_intent_embeddings() -> dict:
    """
    Get or compute embeddings for all intent examples.
    Results are cached to avoid repeated API calls.

    Returns:
        Dictionary mapping intent names to lists of embedding vectors
    """
    global _intent_embeddings_cache

    if not _intent_embeddings_cache:
        for intent_name, examples in INTENT_EXAMPLES.items():
            _intent_embeddings_cache[intent_name] = [
                _get_embedding(example) for example in examples
            ]

    return _intent_embeddings_cache


def classify_intent(chat_history: list) -> Intent:
    """
    Classify the user's intent from the chat history using semantic search.

    This function uses OpenAI embeddings to semantically match the user's message
    against example phrases for each intent. The workflow:
    1. Get the user's latest message
    2. Convert it to an embedding
    3. For each intent, compare user embedding to each example and take best score
    4. Pick the intent with the highest score
    5. If score < threshold → UNKNOWN

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
        user_embedding = _get_embedding(latest_message)

        # Get cached embeddings for intent examples
        intent_embeddings = _get_intent_embeddings()

        # Calculate best similarity score for each intent
        intent_scores = {}

        for intent_name, example_embeddings in intent_embeddings.items():
            # Find the highest similarity score among all examples for this intent
            best_score = max(
                _cosine_similarity(user_embedding, example_emb)
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