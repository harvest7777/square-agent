import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
