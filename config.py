import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 

if GOOGLE_API_KEY is None:
    raise ValueError("Please provide the Google API Key")

print("Google API Key loaded successfully!")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if TAVILY_API_KEY is None:
    raise ValueError("Tavily API Key not found.")

MODEL_NAME = "gemini-2.5-flash"
DATA_FOLDER = "data"

UPLOAD_FOLDER = "uploads"

LOG_FOLDER = "Logs"

