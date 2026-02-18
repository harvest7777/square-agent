## Square OAuth Setup

Configure the environment variables displayed in the Square Developer dashboard under **OAuth**:

Also ensure your `.env` includes any required non-OAuth variables from `.env.example` (e.g. `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` if you're using Supabase).

```
SQUARE_REDIRECT_URI=your_redirect_uri
SQUARE_CLIENT_ID=your_client_id
SQUARE_CLIENT_SECRET=your_client_secret
```

![Square OAuth tab showing redirect URI and client credentials](2026-02-03-13-35-49.png)

## OAuth happy path (end-to-end)

Use `services/oauth_happy_path.py` to run through the full exchange and see the bearer token (and related data) printed in the terminal.

1. **Start the FastAPI server** (redirect must be `http://localhost:3000/square/callback` in your Square app and in `.env`):

   ```bash
   python -m services.oauth_happy_path
   ```

2. **Open the auth URL** shown in the terminal (e.g. copy “Authorize here: …” and open it in your browser).

3. **Have the Square Dashboard open** for the sandbox account you want a token for. Use **Sandbox Test Accounts** in the Square Developer dashboard and open that account’s “Square Dashboard” link in another tab so you’re already signed in.

4. **Complete the OAuth flow** in the browser (approve the app for that account). You’ll be redirected to `http://localhost:3000/square/callback?code=...`.

5. **In the terminal** where the server is running, you’ll see the exchange result printed: `merchant_id`, `bearer_token`, `refresh_token`, and `expires_at`. That’s the happy path.

## Local testing checklist

- Ensure at least one sandbox test account is active.
- Open the corresponding Square Dashboard in a browser tab before kicking off OAuth flows.
- Use the **Sandbox Test Accounts** section in Square Developer to jump directly into each account’s dashboard.

![Sandbox test accounts list with dashboard link highlighted](2026-02-03-13-41-23.png)

## Dashboard reference

Keep the dashboard window open while testing so new authorizations apply immediately.

![Square dashboard overview after signing in](2026-02-03-13-42-12.png)
