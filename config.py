import os
from dotenv import load_dotenv

load_dotenv()

IBM_GRANITE_API_KEY = os.getenv("IBM_GRANITE_API_KEY")
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
