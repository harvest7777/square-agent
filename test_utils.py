from square_utils import (
    _format_cents,
    _get_prety_menu_string_from_variation_id,
    _get_variation_info_from_item_id,
    place_order
)
from menu import get_menu, MENU_ITEMS

def test_format_cents():
    print("=== Testing _format_cents ===")
    test_values = [100, 1000, 1550, 99, 0]
    for cents in test_values:
        result = _format_cents(cents)
        print(f"  {cents} cents -> {result}")
    print()

def test_get_menu():
    print("=== Testing get_menu ===")
    menu = get_menu()
    print(menu)

def test_get_pretty_menu_string():
    print("=== Testing _get_prety_menu_string_from_variation_id ===")
    for menu_num, variation_id in MENU_ITEMS.items():
        print(f"  Menu item {menu_num}: {_get_prety_menu_string_from_variation_id(variation_id).strip()}")
    print()

def test_get_variation_info(item_id: str):
    print(f"=== Testing _get_variation_info_from_item_id ({item_id}) ===")
    info = _get_variation_info_from_item_id(item_id)
    print(info)

def test_place_order(variation_id: str):
    print(f"=== Testing place_order ({variation_id}) ===")
    try:
        place_order(variation_id)
        print("  Order placed successfully!")
    except Exception as e:
        print(f"  Error: {e}")
    print()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("SQUARE UTILS TEST SCRIPT")
    print("="*50 + "\n")

    # Test _format_cents (no API call)
    test_format_cents()

    # Test get_menu (requires API)
    test_get_menu()

    # Test _get_prety_menu_string_from_variation_id (requires API)
    test_get_pretty_menu_string()

    # Uncomment to test _get_variation_info_from_item_id with a specific item ID
    catalog_ids = ["CYUVQKK4G4YJZCX26GISIU5A", "3YGHZQN4A4N5W2TFGNKBPF47", "A54LFYWWYJYZJ7DIAU2AXDIW"]
    for item_id in catalog_ids:
        test_get_variation_info(item_id)

    # Uncomment to test place_order (will create a real order in sandbox!)
    test_place_order(MENU_ITEMS[1])
