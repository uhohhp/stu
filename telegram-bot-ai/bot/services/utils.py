# bot/services/utils.py
import re

def markdown_to_html(text: str) -> str:
    """Преобразует простейший markdown в HTML для Telegram."""
    if not text:
        return ""

    # **жирный**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    # *курсив*
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text, flags=re.DOTALL)
    # `код`
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text, flags=re.DOTALL)

    return text

# bot/handlers/utils.py (или drive_service, если хочешь)
import os
from telegram import InputFile
from .drive_service import download_file

async def send_file(update, file_id, lecture_name, description, file_type="slides"):
    """
    Скачивает файл через download_file, отправляет его в Telegram, удаляет после отправки.
    file_type: "audio" или "slides"
    """
    if not file_id:
        await update.message.reply_text(f"❌ Нет {description} для этой лекции.")
        return

    file_path = download_file(file_id, lecture_name, file_type)
    if not file_path:
        await update.message.reply_text(f"❌ Не удалось скачать {description}.")
        return

    try:
        if file_type == "audio":
            print(f"[send_file] Отправка аудио: {lecture_name}.mp3")
            await update.message.reply_audio(
                audio=InputFile(file_path),
                filename=f"{lecture_name}.mp3"
            )
        elif file_type == "slides":
            print(f"[send_file] Отправка PDF: {lecture_name}.pdf")
            await update.message.reply_document(
                document=InputFile(file_path),
                filename=f"{lecture_name}.pdf"
            )
        else:
            print(f"[send_file] Отправка бинарного файла: {lecture_name}")
            await update.message.reply_document(
                document=InputFile(file_path),
                filename=f"{lecture_name}.bin"
            )

        print(f"[send_file] Отправка завершена: {lecture_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отправки {description}: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[send_file] Файл удалён из памяти: {file_path}")