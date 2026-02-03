"""
Script to exchange an OAuth authorization code for a bearer token.

This is Step 4 in the OAuth workflow:
1. get_auth_link.py → generates auth URL
2. User authorizes → redirected with code
3. Callback receives code
4. THIS SCRIPT → exchanges code for bearer token
5. get_store_data.py → uses token to fetch data

Usage:
    python services/exchange_code_for_token.py <authorization_code>

Example:
    python services/exchange_code_for_token.py sq0cgb-ABC123XYZ
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Square OAuth configuration
SQUARE_SANDBOX_ID = os.environ.get("SQUARE_SANDBOX_ID")
SQUARE_SANDBOX_SECRET = os.environ.get("SQUARE_SANDBOX_SECRET")
REDIRECT_URI = "http://localhost:3000/square/callback"
TOKEN_URL = "https://connect.squareupsandbox.com/oauth2/token"


def exchange_code_for_token(authorization_code: str) -> dict:
    """
    Exchange an authorization code for OAuth access and refresh tokens.

    Args:
        authorization_code: The code received from Square's OAuth callback

    Returns:
        Dictionary containing access_token, refresh_token, merchant_id, etc.

    Raises:
        ValueError: If required environment variables are missing
        Exception: If the token exchange fails
    """
    if not SQUARE_SANDBOX_ID:
        raise ValueError("SQUARE_SANDBOX_ID not found in environment variables")
    if not SQUARE_SANDBOX_SECRET:
        raise ValueError("SQUARE_SANDBOX_SECRET not found in environment variables")

    payload = {
        "client_id": SQUARE_SANDBOX_ID,
        "client_secret": SQUARE_SANDBOX_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Content-Type": "application/json",
        "Square-Version": "2026-01-22"
    }

    response = requests.post(TOKEN_URL, json=payload, headers=headers)
    data = response.json()

    if response.status_code != 200 or "errors" in data:
        errors = data.get("errors", [{"detail": "Unknown error"}])
        error_msg = errors[0].get("detail", str(errors))
        raise Exception(f"Token exchange failed: {error_msg}")

    return data


def display_token_info(token_data: dict) -> None:
    """Display the token information in a formatted way."""
    print("\n" + "=" * 60)
    print("TOKEN EXCHANGE SUCCESSFUL")
    print("=" * 60)

    print(f"\nAccess Token:  {token_data.get('access_token', 'N/A')}")
    print(f"Token Type:    {token_data.get('token_type', 'N/A')}")
    print(f"Expires At:    {token_data.get('expires_at', 'N/A')}")
    print(f"Merchant ID:   {token_data.get('merchant_id', 'N/A')}")
    print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')}")
    print(f"Short Lived:   {token_data.get('short_lived', False)}")

    print("\n" + "-" * 60)
    print("Add this to your .env file:")
    print("-" * 60)
    print(f"BEARER_TOKEN = {token_data.get('access_token', '')}")
    print(f"REFRESH_TOKEN = {token_data.get('refresh_token', '')}")
    print(f"MERCHANT_ID = {token_data.get('merchant_id', '')}")


def main():
    """Main function to exchange authorization code for tokens."""
    if len(sys.argv) < 2:
        print("Usage: python services/exchange_code_for_token.py <authorization_code>")
        print("\nExample:")
        print("  python services/exchange_code_for_token.py sq0cgb-ABC123XYZ")
        print("\nThe authorization code is the 'code' parameter from your callback URL:")
        print("  http://localhost:3000/square/callback?code=<THIS_VALUE>&state=...")
        sys.exit(1)

    authorization_code = sys.argv[1]

    print("Exchanging authorization code for bearer token...")
    print(f"Code: {authorization_code[:10]}..." if len(authorization_code) > 10 else f"Code: {authorization_code}")

    try:
        token_data = exchange_code_for_token(authorization_code)
        display_token_info(token_data)

        print("\n" + "=" * 60)
        print("SUCCESS: You can now run get_store_data.py")
        print("=" * 60)

        return {"success": True, "data": token_data}

    except ValueError as e:
        print(f"\nCONFIGURATION ERROR: {e}")
        print("Make sure SQUARE_SANDBOX_ID and SQUARE_SANDBOX_SECRET are set in your .env file.")
        return {"success": False, "error": str(e)}

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPossible causes:")
        print("  - The authorization code has already been used")
        print("  - The authorization code has expired")
        print("  - Invalid client credentials")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
