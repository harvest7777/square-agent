"""
Square API Client

A unified client for interacting with the Square API.
Wraps catalog, location, and order operations behind a single interface
with a shared SDK client instance and cached location ID.

The token parameter accepts a bearer token obtained from Square's OAuth flow.
Use SquareOAuth to authenticate a merchant, then pass the resulting
access_token directly to SquareClient:

    from services.square_oauth import SquareOAuth
    from services.square_client import SquareClient

    # 1. OAuth flow — merchant authorizes your app
    oauth = SquareOAuth(
        client_id="sq0idp-xxx",
        client_secret="sq0csp-xxx",
        redirect_uri="https://yourapp.com/square/callback",
    )
    tokens = oauth.exchange_code(code="sq0cgb-xxx")

    # 2. Use the merchant's bearer token to interact with their store
    client = SquareClient(token=tokens.access_token)

    items = client.list_catalog_items()
    order_id = client.place_order(variation_id="...")
    locations = client.list_locations()
"""

import uuid
from typing import Literal

from square import Square
from square.environment import SquareEnvironment


class SquareClient:
    """
    Unified Square API client.

    Holds a single SDK client instance and caches the primary location ID
    so individual operations don't need to re-fetch it.
    """

    def __init__(
        self,
        token: str,
        environment: Literal["sandbox", "production"] = "sandbox",
    ):
        if not token or not token.strip():
            raise ValueError("token is required")

        self._environment = environment
        self._sdk = Square(
            token=token.strip(),
            environment=(
                SquareEnvironment.SANDBOX
                if environment == "sandbox"
                else SquareEnvironment.PRODUCTION
            ),
        )
        self._location_id: str | None = None

    # ── Locations ────────────────────────────────────────────

    def _get_primary_location_id(self) -> str:
        """Return the cached primary location ID, fetching it once if needed."""
        if self._location_id is None:
            locations = self.list_locations()
            if not locations:
                raise RuntimeError("No locations found for this Square account")
            self._location_id = locations[0]["id"]
        return self._location_id

    def list_locations(self) -> list[dict]:
        """List all locations for the merchant."""
        response = self._sdk.locations.list()

        if response.errors:
            raise RuntimeError(f"Failed to fetch locations: {response.errors}")

        locations = []
        for loc in response.locations or []:
            address = loc.address
            address_str = "No address"
            if address:
                parts = [
                    getattr(address, "address_line_1", None),
                    getattr(address, "address_line_2", None),
                    getattr(address, "locality", None),
                    getattr(address, "administrative_district_level_1", None),
                    getattr(address, "postal_code", None),
                ]
                address_str = ", ".join(filter(None, parts)) or "No address"

            locations.append({
                "id": loc.id,
                "name": loc.name,
                "address": address_str,
                "status": loc.status,
                "type": getattr(loc, "type", "N/A"),
                "business_name": getattr(loc, "business_name", "N/A"),
            })

        return locations

    # ── Catalog ──────────────────────────────────────────────

    def list_catalog_items(self) -> list[dict]:
        """
        List all catalog items with their variations.

        Returns a list of dicts with id, name, description, and variations.
        Each variation has id, name, and formatted price.
        """
        items = []

        for obj in self._sdk.catalog.list(types=["ITEM"]):
            if obj.type != "ITEM":
                continue

            item_data = obj.item_data
            variations = []

            for var in getattr(item_data, "variations", []) or []:
                var_data = var.item_variation_data
                price = None
                price_money = getattr(var_data, "price_money", None)
                if price_money:
                    price = getattr(price_money, "amount", None)

                variations.append({
                    "id": var.id,
                    "name": getattr(var_data, "name", "Unnamed"),
                    "price_cents": price,
                    "price": _format_cents(price),
                })

            items.append({
                "id": obj.id,
                "name": getattr(item_data, "name", "Unnamed"),
                "description": getattr(item_data, "description", None),
                "variations": variations,
            })

        return items

    def get_item(self, item_id: str) -> dict:
        """
        Get a catalog item by ID with all its variations.

        Returns a dict with name and a list of variation dicts
        (each with id, name, price_cents, price).
        """
        response = self._sdk.catalog.object.get(object_id=item_id)
        item_data = response.object.item_data
        item_name = item_data.name

        variations = []
        for var in item_data.variations:
            var_data = var.item_variation_data
            price = var_data.price_money.amount
            variations.append({
                "id": var.id,
                "name": var_data.name,
                "price_cents": price,
                "price": _format_cents(price),
            })

        return {"name": item_name, "variations": variations}

    def get_variation(self, variation_id: str) -> dict:
        """
        Get a catalog variation by ID, including its parent item name.

        Returns a dict with item_name, variation_name, price_cents, and price.
        """
        response = self._sdk.catalog.object.get(object_id=variation_id)

        if response.object.type != "ITEM_VARIATION":
            raise ValueError("The variation_id must link to an ITEM_VARIATION")

        data = response.object.item_variation_data
        base_item_id = data.item_id
        base_item_name = (
            self._sdk.catalog.object.get(object_id=base_item_id)
            .object.item_data.name
        )

        price = data.price_money.amount

        return {
            "item_name": base_item_name,
            "variation_name": data.name,
            "price_cents": price,
            "price": _format_cents(price),
        }

    # ── Orders ───────────────────────────────────────────────

    def place_order(
        self,
        line_items: list[dict],
        name: str | None = None,
        idempotency_key: str | None = None,
    ) -> str:
        """
        Place an order with one or more line items.

        Args:
            line_items: List of dicts, each with "variation_id" and
                        optional "quantity" (defaults to "1").
            name: Optional display name for the order (e.g. "Fetch.ai Event").
            idempotency_key: Unique key to prevent duplicate orders.
                             Auto-generated if not provided.

        Returns:
            The created order ID.
        """
        if not line_items:
            raise ValueError("line_items must not be empty")

        if idempotency_key is None:
            idempotency_key = str(uuid.uuid4())

        location_id = self._get_primary_location_id()

        order = {
            "location_id": location_id,
            "line_items": [
                {
                    "catalog_object_id": item["variation_id"],
                    "quantity": item.get("quantity", "1"),
                }
                for item in line_items
            ],
            "fulfillments": [
                {
                    "type": "PICKUP",
                    "state": "PROPOSED",
                    "pickup_details": {
                        "recipient": {
                            "display_name": name or "API Order"
                        },
                        "schedule_type": "ASAP",
                    },
                }
            ],
        }

        if name:
            order["reference_id"] = name

        response = self._sdk.orders.create(
            idempotency_key=idempotency_key,
            order=order,
        )

        if response.errors:
            raise RuntimeError(f"Failed to place order: {response.errors}")

        return response.order.id


# ── Helpers ──────────────────────────────────────────────────

def _format_cents(cents: int | None) -> str:
    """Convert cents to a dollar-formatted string."""
    if cents is None:
        return "Price not set"
    return f"${cents / 100.0:.2f}"
