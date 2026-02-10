from graph.state import OrderState
from services.llm_client import client

VALID_INTENTS = ["view_menu", "add_item", "view_cart", "confirm", "cancel", "help", "unknown", "provide_name"]

INTENT_DETECTION_PROMPT = """You are an intent classifier for a food ordering assistant. Analyze the user's message and classify it into exactly one of the following intents:

INTENTS:
- view_menu: User wants to see available items, browse options, or ask what food/drinks are available.
  Examples: "What's on the menu?", "Show me your options", "What do you have?", "What can I order?"

- add_item: User wants to add a specific item to their order or express desire for a food/drink item.
  Examples: "I'll have a burger", "Add a coffee please", "Can I get fries?", "I want a salad", "Give me two pizzas"

- view_cart: User wants to see what's currently in their order/cart or review their selections.
  Examples: "What's in my cart?", "Show my order", "What did I order?", "Review my items"

- confirm: User is ready to finalize, checkout, or complete their order.
  Examples: "That's all", "I'm done", "Checkout please", "Confirm my order", "Place the order", "Submit"

- cancel: User wants to cancel their order, clear the cart, or start over.
  Examples: "Cancel my order", "Never mind", "Forget it", "Clear everything", "Start over"

- help: User needs assistance, has questions about how to use the system, or is confused.
  Examples: "How does this work?", "Help me", "I'm confused", "What can you do?"

- unknown: The message doesn't clearly fit any of the above intents or is unrelated to ordering.
  Examples: "Hello", "What's the weather?", random text, gibberish

INSTRUCTIONS:
- Respond with ONLY the intent name (e.g., "add_item")
- Choose the single most likely intent based on the user's message
- If the message contains both a question and an order, prioritize the order (add_item)
- When in doubt between intents, prefer "unknown" over guessing

User message: {user_input}

Intent:"""


NAME_EXTRACTION_PROMPT = """Extract just the person's name from the following message. The user is providing their name for a food order.

Examples:
- "I'm Ryan" → Ryan
- "My name is Sarah" → Sarah
- "Ryan" → Ryan
- "Call me Ryan T" → Ryan T
- "it's Alex" → Alex

Respond with ONLY the extracted name, nothing else.

User message: {user_input}

Name:"""


def extract_name(user_input: str) -> str:
    """Extract a person's name from user input using Gemini."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=NAME_EXTRACTION_PROMPT.format(user_input=user_input),
        )
        name = response.text.strip() if response.text else None
        return name if name else user_input.strip()
    except Exception as e:
        print(f"Name extraction error: {e}")
        return user_input.strip()


def detect_intent(user_input: str) -> str:
    """
    LLM-based intent detection using Gemini.

    Analyzes user input to determine their intent in the context of
    a food ordering system.

    Returns one of:
        - "view_menu": User wants to see the menu
        - "add_item": User wants to add something to cart
        - "view_cart": User wants to see their current order
        - "confirm": User wants to confirm/checkout
        - "cancel": User wants to cancel the order
        - "help": User needs help
        - "unknown": Couldn't determine intent
    """
    try:
        from google.genai import types
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=INTENT_DETECTION_PROMPT.format(user_input=user_input),
        )

        intent = response.text.strip().lower() if response.text else None

        # Validate the intent is one of our expected values
        if intent in VALID_INTENTS:
            return intent

        return "unknown"

    except Exception as e:
        # Fallback to unknown on any error
        print(f"Intent detection error: {e}")
        return "unknown"


def classify_intent(state: OrderState) -> dict:
    """
    Node function: Classifies user intent and checks for pending actions.

    This is the entry point for every user message. It:
    1. Detects the intent from user_input
    2. Checks if user has items in cart and is "leaving" the order flow
    3. Adds a warning if so (the "warn and preserve" behavior)

    Returns partial state update with intent and optional warning.
    """
    user_input = state.get("user_input", "")

    # Short-circuit: if we're awaiting a name, extract it and route to confirm
    if state.get("conversation_stage") == "awaiting_name":
        user_name = extract_name(user_input)
        return {
            "intent": "provide_name",
            "user_name": user_name,
            "pending_action_warning": None,
        }

    intent = detect_intent(user_input)

    # Check for pending items when user navigates away
    cart = state.get("cart", [])
    has_pending_items = len(cart) > 0

    # These intents are "leaving" the order flow - user might forget their cart
    leaving_intents = ["view_menu", "help"]

    if has_pending_items and intent in leaving_intents:
        return {
            "intent": intent,
            "pending_action_warning": f"Note: You have {len(cart)} item(s) in your cart."
        }

    # Clear any previous warning
    return {
        "intent": intent,
        "pending_action_warning": None
    }


def route_intent(state: OrderState) -> str:
    """
    Router function: Returns the next node name based on intent.

    This is used with add_conditional_edges to route to the right handler.
    The string returned must match a node name in the graph.
    """
    intent = state.get("intent", "unknown")

    # Map intents to node names
    # These must match the node names added in graph.py
    routes = {
        "view_menu": "show_menu",
        "add_item": "add_to_cart",
        "view_cart": "show_cart",
        "confirm": "collect_name",
        "provide_name": "confirm_order",
        "cancel": "cancel_order",
        "help": "show_help",
        "unknown": "handle_unknown",
    }

    return routes.get(intent, "handle_unknown")
