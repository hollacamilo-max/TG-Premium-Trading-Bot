import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")