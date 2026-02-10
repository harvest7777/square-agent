import json
import os

from dotenv import load_dotenv

from services.square_client import SquareClient
from services.llm_client import client as llm

load_dotenv()

# Module-level client — initialized from the merchant's bearer token
square_client = SquareClient(token=os.environ["BEARER_TOKEN"])

# Cached catalog so we don't hit the API on every menu request
_catalog_cache: list[dict] | None = None


def _get_catalog() -> list[dict]:
    """Fetch and cache the catalog from Square."""
    global _catalog_cache
    if _catalog_cache is None:
        _catalog_cache = square_client.list_catalog_items()
    return _catalog_cache


# ── LLM-based item extraction ───────────────────────────────

# Build a lookup table from variation_id -> cart-ready dict so we can
# validate LLM output against real catalog data instead of trusting it.
def _build_variation_lookup() -> dict[str, dict]:
    """Map every variation_id to its cart-ready dict."""
    lookup = {}
    for item in _get_catalog():
        for var in item.get("variations", []):
            lookup[var["id"]] = {
                "name": f"{item['name']} - {var['name']}",
                "variation_id": var["id"],
                "price_cents": var["price_cents"],
            }
    return lookup


def _format_catalog_for_prompt() -> str:
    """Format the catalog into a readable reference for the LLM prompt."""
    lines = []
    for item in _get_catalog():
        for var in item.get("variations", []):
            lines.append(
                f"- {item['name']} / {var['name']} "
                f"(variation_id: {var['id']}, price: {var['price']})"
            )
    return "\n".join(lines)


ITEM_EXTRACTION_PROMPT = """You are a menu item matcher for a food ordering system.
Given a user's message and the available menu, identify ALL items the user wants to order.

MENU:
{menu}

USER MESSAGE: {user_input}

INSTRUCTIONS:
- Extract every item the user mentions or implies they want to order.
- Match each to the closest menu item and variation.
- If the user doesn't specify a variation, pick the first variation listed.
- If no items match the menu at all, return an empty list.
- Return ONLY valid JSON — no markdown, no explanation.

Response format (JSON array):
[
  {{"variation_id": "EXACT_ID_FROM_MENU"}},
  ...
]

If no items found, return: []

JSON:"""


def find_items(user_input: str) -> list[dict]:
    """
    Use the LLM to extract all menu items from the user's message.

    Returns a list of cart-ready dicts (name, variation_id, price_cents),
    or an empty list if nothing matched.
    """
    catalog = _get_catalog()
    if not catalog:
        return []

    menu_text = _format_catalog_for_prompt()
    prompt = ITEM_EXTRACTION_PROMPT.format(menu=menu_text, user_input=user_input)

    try:
        response = llm.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw = response.text.strip() if response.text else "[]"
        # Strip markdown code fences the LLM sometimes adds
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        parsed = json.loads(raw)

        if not isinstance(parsed, list):
            return []

        # Validate each variation_id against the real catalog
        lookup = _build_variation_lookup()
        matched = []
        for entry in parsed:
            vid = entry.get("variation_id")
            if vid and vid in lookup:
                matched.append(lookup[vid])

        return matched

    except (json.JSONDecodeError, Exception) as e:
        print(f"Item extraction error: {e}")
        return []


def format_menu() -> str:
    """Format the Square catalog for display."""
    catalog = _get_catalog()

    if not catalog:
        return "The menu is currently unavailable."

    lines = ["Here's our menu:\n"]
    for item in catalog:
        lines.append(f"\n{item['name']}:")
        if item.get("description"):
            lines.append(f"  {item['description']}")
        for var in item.get("variations", []):
            lines.append(f"  - {var['name']}: {var['price']}")

    return "\n".join(lines)