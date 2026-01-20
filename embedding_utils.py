import os
from openai import OpenAI
from dotenv import load_dotenv
from intent_examples import INTENT_EXAMPLES

load_dotenv()

# Initialize OpenAI client - API key will be loaded from environment
# Set OPENAI_API_KEY in your .env file
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding model to use
EMBEDDING_MODEL = "text-embedding-3-small"

# Cache for intent example embeddings (computed once)
_intent_embeddings_cache = {}


def get_embedding(text: str) -> list:
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
