import os
from google import genai


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY is None:
    raise ValueError("Can't find the API Key LOL")

DEFAULT_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GOOGLE_API_KEY)