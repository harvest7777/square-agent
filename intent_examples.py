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

# Similarity threshold - below this returns UNKNOWN
SIMILARITY_THRESHOLD = 0.3
