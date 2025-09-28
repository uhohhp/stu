import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TG_TOKEN = os.getenv('TG_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR/"data.sqlite3"}')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
GEMINI_API_KEY = os.getenv('DEEPSEEK_API_KEY')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')