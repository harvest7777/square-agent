import json
import os

from dotenv import load_dotenv

from services.square_client import SquareClient
from services.llm_client import client as llm

load_dotenv()

# Module-level client — initialized from the merchant's bearer token
square_client = SquareClient(token=os.environ["BEARER_TOKEN"], environment=os.environ["ENVIRONMENT"])

# Set to True to bypass the allowlist and show the full catalog.
# SHOW_ALL_PRODUCTS: bool = True 
SHOW_ALL_PRODUCTS: bool = False

# Variation-level allowlist: only these variations (and their parent items)
# are visible in the menu and orderable. Update before each event.
ALLOWED_VARIATION_IDS: set[str] = {
    "2ARY3CNUY2XK3HBYQWU5VCK5",  # Tira-Miss-U
    "ON7E4JRX37X6UNHRTJKM5S35",  # Cardinal Chai
    "AGPGES5WOERWCEKPVC7T4QF3",  # Pep-in-yo-step
    "AKEWKQSK5JQXMUQPUE3VAEOE",  # Karl the Fog
    "ALRYZAS3HLYQHHE5U6XG4WVM",  # Love You So Matcha
}

# Cached catalog so we don't hit the API on every menu request
_catalog_cache: list[dict] | None = None


def _get_catalog() -> list[dict]:
    """Fetch and cache the catalog from Square, filtered to allowed variations."""
    global _catalog_cache
    if _catalog_cache is None:
        full_catalog = square_client.list_catalog_items()
        if SHOW_ALL_PRODUCTS:
            _catalog_cache = full_catalog
        else:
            filtered = []
            for item in full_catalog:
                allowed_vars = [
                    v for v in item.get("variations", [])
                    if v["id"] in ALLOWED_VARIATION_IDS
                ]
                if allowed_vars:
                    filtered.append({**item, "variations": allowed_vars})
            _catalog_cache = filtered
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
Given a user's message and the available menu, identify the ONE item the user wants to order.

MENU:
{menu}

USER MESSAGE: {user_input}

INSTRUCTIONS:
- Extract only the single most prominent item the user mentions or implies they want to order.
- Match it to the closest menu item and variation.
- If the user doesn't specify a variation, pick the first variation listed.
- If no items match the menu at all, return an empty list.
- Return at most one item in the array.
- Return ONLY valid JSON — no markdown, no explanation.

Response format (JSON array):
[
  {{"variation_id": "EXACT_ID_FROM_MENU"}}
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


def _format_cents_display(cents: int) -> str:
    """Format cents as $xx.xx for menu display."""
    return f"${cents / 100.0:.2f}"


def format_menu(*, simple: bool = True) -> str:
    """Format the Square catalog for display.

    When simple is True, each line is: $xx.xx - Item Name - Variation Name.
    When simple is False, full menu with descriptions and numbered items.
    """
    catalog = _get_catalog()

    if not catalog:
        return "The menu is currently unavailable."

    if simple:
        # Double newlines for line breaks; " = " separator so markdown doesn't strip it.
        parts = ["Here's our menu", "=============", ""]
        for item in catalog:
            for var in item.get("variations", []):
                price = var.get("price") or _format_cents_display(var.get("price_cents", 0))
                parts.append(f"  {price} = {item['name']}")
        return "\n\n".join(parts) if len(parts) > 3 else "The menu is currently unavailable."

    # Markdown-friendly: equals underline = heading, " = " separator, • for bullets.
    lines = [
        "Here's our menu",
        "=============",
        ""
    ]
    n = 1
    for item in catalog:
        lines.append(f"  {n}. {item['name']}")
        if item.get("description"):
            lines.append(f"     {item['description']}")
        for var in item.get("variations", []):
            price = var.get("price") or _format_cents_display(var.get("price_cents", 0))
            lines.append(f"     • {var['name']} = {price}")
        lines.append("")
        n += 1
    lines.append("Say an item name to add it, or 'cart' / 'confirm' when ready.")
    return "\n\n".join(lines).strip()