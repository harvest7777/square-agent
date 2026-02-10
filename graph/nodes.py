from graph.state import OrderState
from graph.data import format_menu, find_items, square_client


def _format_cents(cents: int) -> str:
    """Convert cents to a dollar-formatted string."""
    return f"${cents / 100.0:.2f}"


def _build_response(message: str, warning: str | None) -> str:
    """Helper to prepend warning to response if present."""
    if warning:
        return f"{warning}\n\n{message}"
    return message


def show_menu(state: OrderState) -> dict:
    """Display the menu to the user."""
    warning = state.get("pending_action_warning")
    menu_text = format_menu()

    return {
        "bot_response": _build_response(menu_text, warning),
        "conversation_stage": "browsing"
    }


def add_to_cart(state: OrderState) -> dict:
    """Parse items from user input and add them to cart."""
    user_input = state.get("user_input", "")
    cart = state.get("cart", []).copy()

    items = find_items(user_input)

    if not items:
        return {
            "bot_response": "I couldn't find any matching items on the menu. "
                           "Try saying 'menu' to see what's available.",
            "conversation_stage": "ordering"
        }

    cart.extend(items)
    total = sum(i["price_cents"] for i in cart)

    added_lines = [f"  - {item['name']} ({_format_cents(item['price_cents'])})" for item in items]
    added_text = "\n".join(added_lines)

    return {
        "cart": cart,
        "bot_response": f"Added {len(items)} item(s) to your cart:\n{added_text}\n\n"
                       f"Cart total: ~~{_format_cents(total)}~~ $0.00\n"
                       f"On behalf of Fetch.ai, your total is free for this event!\n\n"
                       f"Say 'confirm' to checkout, 'cart' to see your order, or keep adding items.",
        "conversation_stage": "ordering"
    }


def show_cart(state: OrderState) -> dict:
    """Display the current cart contents."""
    cart = state.get("cart", [])

    if not cart:
        return {
            "bot_response": "Your cart is empty. Say 'menu' to see what's available!",
            "conversation_stage": "idle"
        }

    lines = ["Your current order:\n"]
    for i, item in enumerate(cart, 1):
        lines.append(f"  {i}. {item['name']} - {_format_cents(item['price_cents'])}")

    total = sum(item["price_cents"] for item in cart)
    lines.append(f"\nTotal: {_format_cents(total)}")
    lines.append("\nSay 'confirm' to checkout or 'cancel' to clear your cart.")

    return {
        "bot_response": "\n".join(lines),
        "conversation_stage": "ordering"
    }


def collect_name(state: OrderState) -> dict:
    """Ask the user for their name before placing the order."""
    cart = state.get("cart", [])

    if not cart:
        return {
            "bot_response": "Your cart is empty! Add some items before confirming.\n"
                           "Say 'menu' to see what's available.",
            "conversation_stage": "idle"
        }

    return {
        "bot_response": "What's your name for this order?",
        "conversation_stage": "awaiting_name"
    }


def confirm_order(state: OrderState) -> dict:
    """Confirm and place the order via Square (no payment — event-covered)."""
    cart = state.get("cart", [])

    if not cart:
        return {
            "bot_response": "Your cart is empty! Add some items before confirming.\n"
                           "Say 'menu' to see what's available.",
            "conversation_stage": "idle"
        }

    user_name = state.get("user_name", "Guest")
    order_name = f"{user_name} - Fetch.ai Event"

    line_items = [
        {"variation_id": item["variation_id"]}
        for item in cart
    ]
    order_id = square_client.place_order(line_items=line_items, name=order_name)

    total = sum(item["price_cents"] for item in cart)
    item_count = len(cart)

    return {
        "cart": [],
        "user_name": None,
        "bot_response": f"Order confirmed! You ordered {item_count} item(s).\n"
                       f"Total: ~~{_format_cents(total)}~~ $0.00\n"
                       f"On behalf of Fetch.ai, your total is free for this event!\n\n"
                       f"Order ID: {order_id}\n"
                       f"Thank you for your order!\n\n"
                       f"Say 'menu' to start a new order.",
        "conversation_stage": "idle"
    }


def cancel_order(state: OrderState) -> dict:
    """Cancel the current order and clear the cart."""
    cart = state.get("cart", [])

    if not cart:
        return {
            "bot_response": "Nothing to cancel - your cart is already empty.\n"
                           "Say 'menu' to see what's available.",
            "conversation_stage": "idle"
        }

    item_count = len(cart)
    return {
        "cart": [],
        "bot_response": f"Order cancelled. Removed {item_count} item(s) from your cart.\n"
                       f"Say 'menu' to start over.",
        "conversation_stage": "idle"
    }


def show_help(state: OrderState) -> dict:
    """Display help information."""
    warning = state.get("pending_action_warning")

    help_text = """Here's how to use this ordering system:

Commands:
  - 'menu'    - See what's available
  - 'cart'    - View your current order
  - 'add X'   - Add item X to your cart (e.g., 'add burger')
  - 'confirm' - Place your order
  - 'cancel'  - Clear your cart and start over
  - 'quit'    - Exit the application

Just type naturally! For example:
  - "I'll have a cheese burger"
  - "Show me the menu"
  - "What's in my cart?"
  - "That's all, checkout please" """

    return {
        "bot_response": _build_response(help_text, warning),
        "conversation_stage": state.get("conversation_stage", "idle")
    }


def handle_unknown(state: OrderState) -> dict:
    """Handle unrecognized input."""
    return {
        "bot_response": "Hmm, I didn't quite catch that! This is the Fetch.ai Coffee x On Call event bot — "
                       "I'm here to help you order drinks. Say 'menu' to see what's available, or 'help' for all commands. "
                       "What would you like?",
        "conversation_stage": state.get("conversation_stage", "idle")
    }
