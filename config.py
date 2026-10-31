import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in the project .env file.")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

MODEL_NAME = "gemini-2.5-flash"
DATA_FOLDER = PROJECT_ROOT / "data"
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
LOG_FOLDER = PROJECT_ROOT / "Logs"
