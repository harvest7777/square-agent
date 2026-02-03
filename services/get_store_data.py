
import os
from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()

def get_square_client() -> Square:
    bearer_token = os.environ.get("BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("BEARER_TOKEN not found in environment variables")

    return Square(
        token=bearer_token,
        environment=SquareEnvironment.SANDBOX
    )


def format_cents(cents: int) -> str:
    if cents is None:
        return "Price not set"
    dollars = cents / 100.0
    return f"${dollars:.2f}"


def fetch_locations(client: Square) -> list:
    response = client.locations.list()

    if response.errors:
        raise Exception(f"Failed to fetch locations: {response.errors}")

    locations = []
    for loc in response.locations or []:
        address = loc.address
        address_str = "No address"
        if address:
            try:
                parts = [
                    getattr(address, 'address_line_1', None),
                    getattr(address, 'address_line_2', None),
                    getattr(address, 'locality', None),
                    getattr(address, 'administrative_district_level_1', None),
                    getattr(address, 'postal_code', None)
                ]
                address_str = ", ".join(filter(None, parts)) or "No address"
            except Exception:
                address_str = str(address) if address else "No address"

        locations.append({
            "id": loc.id,
            "name": loc.name,
            "address": address_str,
            "status": loc.status,
            "type": getattr(loc, 'type', 'N/A'),
            "business_name": getattr(loc, 'business_name', 'N/A')
        })

    return locations


def fetch_catalog_items(client: Square) -> list:
    
    items = []

    # catalog.list returns a pager, iterate through it
    for obj in client.catalog.list(types=["ITEM"]):
        if obj.type != "ITEM":
            continue

        item_data = obj.item_data
        variations = []

        for var in getattr(item_data, 'variations', []) or []:
            var_data = var.item_variation_data
            price = None
            price_money = getattr(var_data, 'price_money', None)
            if price_money:
                price = getattr(price_money, 'amount', None)

            variations.append({
                "id": var.id,
                "name": getattr(var_data, 'name', 'Unnamed'),
                "price": format_cents(price)
            })

        items.append({
            "id": obj.id,
            "name": getattr(item_data, 'name', 'Unnamed'),
            "description": getattr(item_data, 'description', None),
            "variations": variations
        })

    return items


def display_locations(locations: list) -> None:
    """Display locations in a formatted way."""
    print("\n" + "=" * 60)
    print("STORE LOCATIONS")
    print("=" * 60)

    if not locations:
        print("No locations found.")
        return

    for i, loc in enumerate(locations, 1):
        print(f"\n[{i}] {loc['name']}")
        print(f"    Business: {loc['business_name']}")
        print(f"    Address:  {loc['address']}")
        print(f"    Type:     {loc['type']}")
        print(f"    Status:   {loc['status']}")
        print(f"    ID:       {loc['id']}")


def display_menu_items(items: list) -> None:
    """Display menu items in a formatted way."""
    print("\n" + "=" * 60)
    print("MENU ITEMS")
    print("=" * 60)

    if not items:
        print("No menu items found.")
        return

    for i, item in enumerate(items, 1):
        print(f"\n[{i}] {item['name']}")
        if item['description']:
            print(f"    Description: {item['description']}")

        if item['variations']:
            print("    Variations:")
            for var in item['variations']:
                print(f"      - {var['name']}: {var['price']}")
        else:
            print("    No variations")


def main():
    print("Connecting to Square API...")

    try:
        client = get_square_client()
        print("Successfully connected with OAuth token.")

        # Fetch locations
        print("\nFetching store locations...")
        locations = fetch_locations(client)
        display_locations(locations)

        # Fetch menu items
        print("\nFetching menu items...")
        items = fetch_catalog_items(client)
        display_menu_items(items)

        print("\n" + "=" * 60)
        print("SUCCESS: Square data retrieved successfully!")
        print("=" * 60)

        return {
            "success": True,
            "locations": locations,
            "items": items
        }

    except ValueError as e:
        print(f"\nCONFIGURATION ERROR: {e}")
        print("Make sure BEARER_TOKEN is set in your .env file.")
        return {"success": False, "error": str(e)}

    except Exception as e:
        print(f"\nERROR: {e}")
        print("The OAuth token may be invalid or expired.")
        print("Please re-authenticate with Square to get a new token.")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
