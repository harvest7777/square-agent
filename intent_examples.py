# Example phrases for each intent (used for semantic matching)
INTENT_EXAMPLES = {
    "PLACE_ORDER": [
        "I'll take item 1",
        "Give me the second one",
        "I want number 2",
        "Order the first item please",
        "Can I get item 3",
        "I'd like to have the third option",
        "Let me get number one",
        "I'll have the second drink",
        "Put in an order for item 2",
        "I want to buy the first one",
    ],
    "WANT_TO_ORDER": [
        "Show me the menu",
        "What do you have",
        "What's available",
        "I want to order something",
        "What are my options",
        "Can I see what you offer",
        "What drinks do you have",
        "Help me order",
        "I'm interested in ordering",
        "What can I get here",
    ],
}

# Example phrases for each menu item number (used for semantic matching)
MENU_ITEM_EXAMPLES = {
    1: [
        "I want the first one",
        "Give me item 1",
        "The first option please",
        "Number one",
        "I'll take the first",
        "Item number 1",
        "The 1st one",
        "Option one please",
        "I'd like the first item",
        "Let me have the first drink",
    ],
    2: [
        "I want the second one",
        "Give me item 2",
        "The second option please",
        "Number two",
        "I'll take the second",
        "Item number 2",
        "The 2nd one",
        "Option two please",
        "I'd like the second item",
        "Let me have the second drink",
    ],
    3: [
        "I want the third one",
        "Give me item 3",
        "The third option please",
        "Number three",
        "I'll take the third",
        "Item number 3",
        "The 3rd one",
        "Option three please",
        "I'd like the third item",
        "Let me have the third drink",
    ],
}

# Similarity threshold - below this returns UNKNOWN
SIMILARITY_THRESHOLD = 0.3

# Similarity threshold for menu item matching
MENU_ITEM_SIMILARITY_THRESHOLD = 0.3
