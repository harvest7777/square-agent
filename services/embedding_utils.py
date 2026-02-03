import os
from openai import OpenAI
from dotenv import load_dotenv
from core.intent_examples import INTENT_EXAMPLES, MENU_ITEM_EXAMPLES

load_dotenv()


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding model to use
EMBEDDING_MODEL = "text-embedding-3-small"

_intent_embeddings_cache = {}

_menu_item_embeddings_cache = {}


def get_embedding(text: str) -> list:
    
    text = text.replace("\n", " ").strip()
    response = openai_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def cosine_similarity(vec1: list, vec2: list) -> float:
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def get_intent_embeddings() -> dict:
    
    global _intent_embeddings_cache

    if not _intent_embeddings_cache:
        for intent_name, examples in INTENT_EXAMPLES.items():
            _intent_embeddings_cache[intent_name] = [
                get_embedding(example) for example in examples
            ]

    return _intent_embeddings_cache


def get_menu_item_embeddings() -> dict:
    
    global _menu_item_embeddings_cache

    if not _menu_item_embeddings_cache:
        for item_number, examples in MENU_ITEM_EXAMPLES.items():
            _menu_item_embeddings_cache[item_number] = [
                get_embedding(example) for example in examples
            ]

    return _menu_item_embeddings_cache
