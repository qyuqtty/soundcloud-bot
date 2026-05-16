import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", "downloads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50_000_000))

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверь Environment Variables на Render.")

print("(｡◕‿◕｡) Конфигурация успешно загружена")