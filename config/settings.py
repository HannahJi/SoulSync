import os
from dotenv import load_dotenv
load_dotenv()
# Open AI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Spotify API
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


# LangChain
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")