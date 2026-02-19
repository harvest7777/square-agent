"""
One-time script to aggregate Fetch AI event orders from Square.

Usage:
    BEARER_TOKEN=... SQUARE_LOCATION_ID=... python -m services.total_orders
"""

import os
from collections import defaultdict

from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()


def main():
    token = os.getenv("BEARER_TOKEN")
    location_id = os.getenv("SQUARE_LOCATION_ID")

    client = Square(
        environment=SquareEnvironment.PRODUCTION,
        token=token,
    )

    # Fetch the most recent 1000 orders using cursor-based pagination
    TARGET = 1000
    all_orders = []
    cursor = None
    page = 0

    while len(all_orders) < TARGET:
        page += 1
        fetch = min(TARGET - len(all_orders), 1000)
        kwargs = {
            "location_ids": [location_id],
            "limit": fetch,
            "query": {
                "sort": {"sort_field": "CREATED_AT", "sort_order": "DESC"},
            },
        }
        if cursor:
            kwargs["cursor"] = cursor

        print(f"[page {page}] fetching up to {fetch} orders"
              + (f" (cursor: {cursor[:20]}...)" if cursor else "") + "...")

        response = client.orders.search(**kwargs)

        if response.errors:
            raise RuntimeError(f"Square API error: {response.errors}")

        batch = response.orders or []
        all_orders.extend(batch)
        print(f"[page {page}] got {len(batch)} orders — total so far: {len(all_orders)}")

        cursor = getattr(response, "cursor", None)
        if not cursor:
            print("No more pages.")
            break

    print(f"Done fetching. Total orders retrieved: {len(all_orders)}\n")

    # Filter for Fetch AI orders
    fetch_orders = [o for o in all_orders if _is_fetch_order(o)]

    # Aggregate
    total_money_cents = 0
    total_tip_cents = 0
    item_counts = defaultdict(int)

    for order in fetch_orders:
        total_money_cents += getattr(order.total_money, "amount", 0) or 0
        total_tip_cents += getattr(order.total_tip_money, "amount", 0) or 0

        for item in order.line_items or []:
            key = (getattr(item, "note", None) or getattr(item, "name", None) or "Unknown").strip()
            item_counts[key] += int(item.quantity)

    subtotal_cents = total_money_cents - total_tip_cents

    # Print summary
    print(f"=== Fetch AI Event Order Summary ===")
    print(f"Thanks so much On Call Cafe ^.^\n")
    print(f"Total orders:        {len(fetch_orders)}")
    print(f"Subtotal (excl tip): ${subtotal_cents / 100:.2f}")
    print(f"Tips:                ${total_tip_cents / 100:.2f}")
    print(f"Total charged:       ${total_money_cents / 100:.2f}")
    print(f"\nItems ordered:")
    for item, count in sorted(item_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:>3}x  {item}")


def _is_fetch_order(order) -> bool:
    reference_id = (getattr(order, "reference_id", "") or "").lower()
    ticket_name = (getattr(order, "ticket_name", "") or "").lower()
    return "fetch" in reference_id or "fetch" in ticket_name


if __name__ == "__main__":
    main()
