import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SOURCE_API_URL = os.environ.get("SOURCE_API_URL")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    FILE_SEARCH_STORE_DISPLAY_NAME = os.environ.get("FILE_SEARCH_STORE_DISPLAY_NAME")
    CHAT_MODEL = os.environ.get("CHAT_MODEL", "gemini-2.5-flash")
    ARTICLES_DIR = os.environ.get("ARTICLES_DIR", "articles")
    STATE_FILE = os.environ.get("STATE_FILE", "state.json")
    MAX_ARTICLES = int(os.environ.get("MAX_ARTICLES", "0"))
