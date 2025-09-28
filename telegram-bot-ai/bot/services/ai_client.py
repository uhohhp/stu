import os
import google.generativeai as genai
from ..config import GEMINI_API_KEY  # у нас в config есть эта переменная

# Берём ключ из .env
API_KEY = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
if not API_KEY:
    raise RuntimeError("Нет GEMINI_API_KEY в .env")

# Конфигурируем Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_ai(prompt: str) -> str:
    """Отправляем запрос в Gemini и возвращаем текст ответа."""
    try:
        response = model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text
        return str(response)
    except Exception as e:
        return f"Ошибка: {e}"