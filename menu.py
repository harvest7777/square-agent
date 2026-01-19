from square_utils import _getPrettyMenuStringFromVariationId

# MENU_ITEMS is the canonical truth for what items people can order.
# Each entry maps a menu number to a Square catalog variation ID.
MENU_ITEMS = {
    1: "4YFS323NNR7JDKEDOUBCP6RJ",
    2: "TPPWAJQ4O5FDHUNHX3WMQJG2",
    3: "3BCDXFOJKL3G647HEQYELWK3",
}

def getMenu() -> str:
    """
    Retrieve and format the menu using hardcoded menu items.
    
    Returns:
        Formatted menu string with numbered items and header
    """
    menu_items = []
    for menu_number, variation_id in MENU_ITEMS.items():
        pretty_item = _getPrettyMenuStringFromVariationId(variation_id).strip()
        menu_items.append(pretty_item)
    
    # Format as numbered list with header
    menu = "=======MENU=======\n"
    for i, item in enumerate(menu_items, start=1):
        menu += f"{i}. {item}\n"
    
    return menu