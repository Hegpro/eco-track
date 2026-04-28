import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Admin IDs (Add your Telegram User ID here, comma separated in .env)
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]

# Constants
DB_NAME = os.getenv("DB_NAME", "srihack")
