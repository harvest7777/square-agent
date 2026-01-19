import os
from dotenv import load_dotenv
from square import Square

load_dotenv()

from square.environment import SquareEnvironment

token = os.environ.get("SQUARE_TOKEN")

# NOTE: When switching to production, change `SquareEnvironment.SANDBOX` to `SquareEnvironment.PRODUCTION`
client = Square(
    token=os.environ.get("SQUARE_TOKEN"),
    environment=SquareEnvironment.SANDBOX
)


def _formatCents(cents: int) -> str:
    """
    Convert cents to a formatted USD currency string.
    
    Args:
        cents: Integer value representing the amount in cents (e.g., 1000 for $10.00)
    
    Returns:
        Formatted currency string with dollar sign and two decimal places (e.g., "$10.00")
    """
    dollars = cents / 100.0
    return f"${dollars:.2f}"

def _getPrettyMenuStringFromVariationId(variation_id: str) -> str:

    response = client.catalog.object.get(
    object_id=variation_id
    )

    if response.object.type != "ITEM_VARIATION":
        raise ValueError("The variation_id must link to an ITEM_VARIATION")

    # Get the item name this variation is derived from
    # Ex: variation is eispanner, base item is matcha
    # We want to be able to display matcha - honey oat 
    base_item_id = response.object.item_variation_data.item_id
    base_item_name = client.catalog.object.get(object_id=base_item_id).object.item_data.name

    data = response.object.item_variation_data
    name = data.name
    price = data.price_money.amount
    pretty_item = f"{base_item_name} - {name}: {_formatCents(price)}\n"
    return pretty_item

def _getVariationInfoFromItemId(item_id: str) -> str:
    """
    Developer utility function to retrieve and display item variation information.
    
    This function is intended for developers only to help identify which item variations
    to hardcode in the application. It displays the real-world correlation of each variation,
    including the price, name, variation ID, and how it should appear on the menu.
    
    Args:
        item_id: The catalog object ID for the item whose variations should be retrieved
    
    Returns:
        Formatted string containing all variations with their prices, names, and IDs
    """
    pretty_menu = ""

    response = client.catalog.object.get(
    object_id=item_id
    )
    item_name = response.object.item_data.name
    variations = response.object.item_data.variations

    for variation in variations:
        variation_id = variation.id
        data = variation.item_variation_data
        name = data.name
        price = data.price_money.amount
        pretty_item = f"{item_name} - {name}: {_formatCents(price)} [Variation ID: {variation_id}] \n"
        pretty_menu += pretty_item
    return pretty_menu
    
    
# catalog_ids = ["CYUVQKK4G4YJZCX26GISIU5A","3YGHZQN4A4N5W2TFGNKBPF47","A54LFYWWYJYZJ7DIAU2AXDIW"]
# for c in catalog_ids:
#     print(_getVariationInfoFromItemId(c))
