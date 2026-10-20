import os

import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


store = client.file_search_stores.create(
    config={
        "display_name": "Brainova Class 9",
        "embedding_model": "models/gemini-embedding-2"
    }
)


print("File Search Store created")
print("Name:", store.name)
print("Display name:", store.display_name)