import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_DIR = os.getenv("INPUT_DIR", os.path.join(BASE_DIR, "input"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output"))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure required directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# OpenAI Prompts
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Your default system prompt.")
USER_PROMPT = os.getenv("USER_PROMPT", "Your default user prompt.")
JSON_TEMPLATE = os.getenv("JSON_TEMPLATE", "{}")  # Default empty JSON template

# Flask Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
