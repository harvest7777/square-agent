from enum import Enum


class Intent(str, Enum):
    """Intent enum for user actions."""
    WANT_TO_ORDER = "want to order"
    PLACE_ORDER = "place order"
    UNKNOWN = "unknown"  # Fallback when intent cannot be determined
