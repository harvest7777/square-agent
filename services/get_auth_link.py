import secrets
import urllib.parse

import os

from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("SQUARE_SANDBOX_ID")
REDIRECT_URI = "http://localhost:3000/square/callback"

SCOPES = [
    "BANK_ACCOUNTS_WRITE",
    "BANK_ACCOUNTS_READ",
    "APPOINTMENTS_WRITE",
    "APPOINTMENTS_ALL_WRITE",
    "APPOINTMENTS_READ",
    "APPOINTMENTS_ALL_READ",
    "APPOINTMENTS_BUSINESS_SETTINGS_READ",
    "PAYMENTS_READ",
    "PAYMENTS_WRITE",
    "CASH_DRAWER_READ",
    "ITEMS_WRITE",
    "ITEMS_READ",
    "ORDERS_WRITE",
    "ORDERS_READ",
    "CUSTOMERS_WRITE",
    "CUSTOMERS_READ",
    "DEVICE_CREDENTIAL_MANAGEMENT",
    "DEVICES_READ",
    "DISPUTES_WRITE",
    "DISPUTES_READ",
    "EMPLOYEES_READ",
    "EMPLOYEES_WRITE",
    "GIFTCARDS_READ",
    "GIFTCARDS_WRITE",
    "INVENTORY_WRITE",
    "INVENTORY_READ",
    "INVOICES_WRITE",
    "INVOICES_READ",
    "TIMECARDS_SETTINGS_WRITE",
    "TIMECARDS_SETTINGS_READ",
    "TIMECARDS_WRITE",
    "TIMECARDS_READ",
    "MERCHANT_PROFILE_WRITE",
    "MERCHANT_PROFILE_READ",
    "LOYALTY_READ",
    "LOYALTY_WRITE",
    "PAYMENTS_WRITE_IN_PERSON",
    "PAYMENTS_WRITE_ADDITIONAL_RECIPIENTS",
    "PAYOUTS_READ",
    "ONLINE_STORE_SITE_READ",
    "ONLINE_STORE_SNIPPETS_WRITE",
    "ONLINE_STORE_SNIPPETS_READ",
    "SUBSCRIPTIONS_WRITE",
    "SUBSCRIPTIONS_READ",
    "VENDOR_WRITE",
    "VENDOR_READ",
]

state = secrets.token_urlsafe(16)

params = {
    "client_id": CLIENT_ID,
    "scope": " ".join(SCOPES),
    "redirect_uri": REDIRECT_URI,
    "state": state,
    "session": "false",
}

auth_url = (
    "https://connect.squareupsandbox.com/oauth2/authorize?"
    + urllib.parse.urlencode(params)
)
print(auth_url)