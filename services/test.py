import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager

from services.square_oauth import SquareOAuth

load_dotenv()

oauth = SquareOAuth(
    client_id=os.getenv("SQUARE_CLIENT_ID", ""),
    client_secret=os.getenv("SQUARE_CLIENT_SECRET", ""),
    redirect_uri=os.getenv("SQUARE_REDIRECT_URI", "http://localhost:3000/square/callback"),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth_url, state = oauth.get_auth_url()
    print(f"\nAuthorize here: {auth_url}\n")
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/square/callback")
def square_callback(code: str):
    store_auth_data = oauth.exchange_code(code)
    bearer_token = store_auth_data.access_token
    merchant_id = store_auth_data.merchant_id
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
