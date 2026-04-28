import os
from dotenv import load_dotenv

# Load environment variables from absolute path
base_dir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# Print masked URI for debugging
print(f"DEBUG: Configured MONGO_URI = {MONGO_URI[:25]}...")

# Admin IDs (Add your Telegram User ID here, comma separated in .env)
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]

# Constants
DB_NAME = os.getenv("DB_NAME", "srihack_prod")
