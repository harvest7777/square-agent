"""
Square OAuth Client

A portable, drop-in class for Square OAuth authentication.
Handles the full OAuth flow: auth URL generation, code exchange, and token refresh.

Usage:
    from services.square_oauth import SquareOAuth

    oauth = SquareOAuth(
        client_id="sq0idp-xxx",
        client_secret="sq0csp-xxx",
        redirect_uri="https://yourapp.com/square/callback",
    )

    # Generate auth URL for user to click
    auth_url, state = oauth.get_auth_url()

    # After user approves, exchange code for tokens
    tokens = oauth.exchange_code(code="sq0cgb-xxx")

    # Use tokens with Square SDK
    from square import Square
    client = Square(token=tokens.access_token)
"""

import secrets
import urllib.parse
from dataclasses import dataclass
from typing import Literal

import requests


# OAuth endpoints
SANDBOX_AUTH_URL = "https://connect.squareupsandbox.com/oauth2/authorize"
SANDBOX_TOKEN_URL = "https://connect.squareupsandbox.com/oauth2/token"
PRODUCTION_AUTH_URL = "https://connect.squareup.com/oauth2/authorize"
PRODUCTION_TOKEN_URL = "https://connect.squareup.com/oauth2/token"

# Default scopes - comprehensive list for full API access
DEFAULT_SCOPES = [
    "BANK_ACCOUNTS_READ",
    "BANK_ACCOUNTS_WRITE",
    "APPOINTMENTS_READ",
    "APPOINTMENTS_WRITE",
    "APPOINTMENTS_ALL_READ",
    "APPOINTMENTS_ALL_WRITE",
    "APPOINTMENTS_BUSINESS_SETTINGS_READ",
    "CASH_DRAWER_READ",
    "CUSTOMERS_READ",
    "CUSTOMERS_WRITE",
    "DEVICE_CREDENTIAL_MANAGEMENT",
    "DEVICES_READ",
    "DISPUTES_READ",
    "DISPUTES_WRITE",
    "EMPLOYEES_READ",
    "EMPLOYEES_WRITE",
    "GIFTCARDS_READ",
    "GIFTCARDS_WRITE",
    "INVENTORY_READ",
    "INVENTORY_WRITE",
    "INVOICES_READ",
    "INVOICES_WRITE",
    "ITEMS_READ",
    "ITEMS_WRITE",
    "LOYALTY_READ",
    "LOYALTY_WRITE",
    "MERCHANT_PROFILE_READ",
    "MERCHANT_PROFILE_WRITE",
    "ONLINE_STORE_SITE_READ",
    "ONLINE_STORE_SNIPPETS_READ",
    "ONLINE_STORE_SNIPPETS_WRITE",
    "ORDERS_READ",
    "ORDERS_WRITE",
    "PAYMENTS_READ",
    "PAYMENTS_WRITE",
    "PAYMENTS_WRITE_ADDITIONAL_RECIPIENTS",
    "PAYMENTS_WRITE_IN_PERSON",
    "PAYOUTS_READ",
    "SUBSCRIPTIONS_READ",
    "SUBSCRIPTIONS_WRITE",
    "TIMECARDS_READ",
    "TIMECARDS_WRITE",
    "TIMECARDS_SETTINGS_READ",
    "TIMECARDS_SETTINGS_WRITE",
    "VENDOR_READ",
    "VENDOR_WRITE",
]


class SquareOAuthError(Exception):
    """Raised when Square OAuth operations fail."""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


@dataclass
class OAuthTokens:
    """Container for Square OAuth tokens."""

    access_token: str
    refresh_token: str
    merchant_id: str
    expires_at: str
    token_type: str = "bearer"


class SquareOAuth:
    """
    Square OAuth client for authenticating businesses.

    All configuration is explicit - no hidden environment variables.
    Validates required parameters upfront and fails fast with clear errors.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        environment: Literal["sandbox", "production"] = "sandbox",
        scopes: list[str] | None = None,
    ):
        """
        Initialize the Square OAuth client.

        Args:
            client_id: Square application client ID (from Developer Dashboard)
            client_secret: Square application client secret
            redirect_uri: URL where Square redirects after authorization
            environment: "sandbox" for testing, "production" for live
            scopes: OAuth scopes to request (defaults to comprehensive list)

        Raises:
            ValueError: If any required parameter is missing or empty
        """
        # Validate required parameters upfront
        if not client_id or not client_id.strip():
            raise ValueError("client_id is required")
        if not client_secret or not client_secret.strip():
            raise ValueError("client_secret is required")
        if not redirect_uri or not redirect_uri.strip():
            raise ValueError("redirect_uri is required")
        if environment not in ("sandbox", "production"):
            raise ValueError("environment must be 'sandbox' or 'production'")

        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.redirect_uri = redirect_uri.strip()
        self.environment = environment
        self.scopes = scopes if scopes is not None else DEFAULT_SCOPES

        # Set URLs based on environment
        if environment == "sandbox":
            self._auth_url = SANDBOX_AUTH_URL
            self._token_url = SANDBOX_TOKEN_URL
        else:
            self._auth_url = PRODUCTION_AUTH_URL
            self._token_url = PRODUCTION_TOKEN_URL

    def get_auth_url(self, state: str | None = None) -> tuple[str, str]:
        """
        Generate the OAuth authorization URL.

        Args:
            state: CSRF protection token. Auto-generated if not provided.

        Returns:
            Tuple of (authorization_url, state_token).
            Store the state token to verify the callback.
        """
        if state is None:
            state = secrets.token_urlsafe(16)

        params = {
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state,
            "session": "false",
        }

        url = f"{self._auth_url}?{urllib.parse.urlencode(params)}"
        return url, state

    def exchange_code(self, code: str) -> OAuthTokens:
        """
        Exchange an authorization code for access tokens.

        Args:
            code: The authorization code from the OAuth callback

        Returns:
            OAuthTokens containing access_token, refresh_token, merchant_id, expires_at

        Raises:
            SquareOAuthError: If the token exchange fails
        """
        if not code or not code.strip():
            raise ValueError("code is required")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code.strip(),
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        headers = {
            "Content-Type": "application/json",
            "Square-Version": "2024-01-18",
        }

        response = requests.post(self._token_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            errors = data.get("errors", [{"detail": "Unknown error"}])
            error_detail = errors[0].get("detail", str(errors))
            error_code = errors[0].get("code")
            raise SquareOAuthError(f"Token exchange failed: {error_detail}", error_code)

        return OAuthTokens(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            merchant_id=data["merchant_id"],
            expires_at=data["expires_at"],
            token_type=data.get("token_type", "bearer"),
        )

    def refresh_token(self, refresh_token: str) -> OAuthTokens:
        """
        Refresh an expired access token.

        Args:
            refresh_token: The refresh token from a previous OAuth exchange

        Returns:
            OAuthTokens with new access_token (refresh_token may also be rotated)

        Raises:
            SquareOAuthError: If the refresh fails
        """
        if not refresh_token or not refresh_token.strip():
            raise ValueError("refresh_token is required")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token.strip(),
            "grant_type": "refresh_token",
        }

        headers = {
            "Content-Type": "application/json",
            "Square-Version": "2024-01-18",
        }

        response = requests.post(self._token_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            errors = data.get("errors", [{"detail": "Unknown error"}])
            error_detail = errors[0].get("detail", str(errors))
            error_code = errors[0].get("code")
            raise SquareOAuthError(f"Token refresh failed: {error_detail}", error_code)

        return OAuthTokens(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            merchant_id=data["merchant_id"],
            expires_at=data["expires_at"],
            token_type=data.get("token_type", "bearer"),
        )
