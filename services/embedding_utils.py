import os
from google import genai
from dotenv import load_dotenv
from core.intent_examples import INTENT_EXAMPLES, MENU_ITEM_EXAMPLES

load_dotenv()

# Initialize Gemini client - API key will be loaded from environment
# Set GEMINI_API_KEY in your .env file
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model to use
EMBEDDING_MODEL = "text-embedding-004"

# Cache for intent example embeddings (computed once)
_intent_embeddings_cache = {}

# Cache for menu item example embeddings (computed once)
_menu_item_embeddings_cache = {}


def get_embedding(text: str) -> list:
    """
    Get the embedding vector for a text string using Gemini's embedding model.

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    text = text.replace("\n", " ").strip()
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values


def cosine_similarity(vec1: list, vec2: list) -> float:
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


def get_intent_embeddings() -> dict:
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
                get_embedding(example) for example in examples
            ]

    return _intent_embeddings_cache


def get_menu_item_embeddings() -> dict:
    """
    Get or compute embeddings for all menu item examples.
    Results are cached to avoid repeated API calls.

    Returns:
        Dictionary mapping menu item numbers (int) to lists of embedding vectors
    """
    global _menu_item_embeddings_cache

    if not _menu_item_embeddings_cache:
        for item_number, examples in MENU_ITEM_EXAMPLES.items():
            _menu_item_embeddings_cache[item_number] = [
                get_embedding(example) for example in examples
            ]

    return _menu_item_embeddings_cache
