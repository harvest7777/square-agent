from dotenv import load_dotenv
from square import Square
import os
import uuid

load_dotenv()

from square.environment import SquareEnvironment

token = os.environ.get("SQUARE_TOKEN")

# NOTE: When switching to production, change `SquareEnvironment.SANDBOX` to `SquareEnvironment.PRODUCTION`
client = Square(
    token=os.environ.get("SQUARE_TOKEN"),
    environment=SquareEnvironment.SANDBOX
)


def _format_cents(cents: int) -> str:
    
    dollars = cents / 100.0
    return f"${dollars:.2f}"

def _get_prety_menu_string_from_variation_id(variation_id: str) -> str:

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
    pretty_item = f"{base_item_name} - {name}: {_format_cents(price)}\n"
    return pretty_item

def _get_variation_info_from_item_id(item_id: str) -> str:
    
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
        pretty_item = f"{item_name} - {name}: {_format_cents(price)} [Variation ID: {variation_id}] \n"
        pretty_menu += pretty_item
    return pretty_menu


def place_order(variation_id: str, idempotency_key: str = None) -> None:
    
    if idempotency_key is None:
        idempotency_key = str(uuid.uuid4())
        print(idempotency_key)

    # TODO: Make this locations retrieve from .env
    locations_response = client.locations.list()
    if not locations_response.locations:
        raise Exception("No locations found for this Square account")
    location_id = locations_response.locations[0].id

    response = client.orders.create(
        idempotency_key=idempotency_key,
        order={
            "location_id": location_id,
            "line_items": [
                {
                    "catalog_object_id": variation_id,
                    "quantity": "1"
                }
            ]
        }
    )

    if response.errors:
        raise Exception(f"Failed to place order: {response.errors}")
    
    order_id = response.order.id
    print(f"Order placed successfully! Order ID: {order_id}")
    
# catalog_ids = ["CYUVQKK4G4YJZCX26GISIU5A","3YGHZQN4A4N5W2TFGNKBPF47","A54LFYWWYJYZJ7DIAU2AXDIW"]
# for c in catalog_ids:
#     print(_getVariationInfoFromItemId(c))

place_order("TPPWAJQ4O5FDHUNHX3WMQJG2")
