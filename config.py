import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOADS_DIR = Path(os.getenv("DOWNLOADS_DIR", "downloads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50_000_000))

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

print("(｡◕‿◕｡) Конфигурация успешно загружена")