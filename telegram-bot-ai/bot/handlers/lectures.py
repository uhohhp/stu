# bot/handlers/lectures.py
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from ..db import get_db_session, lectures
from ..services.drive_service import download_file_from_drive


# ------------------------
# показать список тем
async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_db_session()
    topics = session.query(lectures.c.topic).distinct().all()
    session.close()

    keyboard = [[t[0]] for t in topics]
    await update.message.reply_text(
        "Выберите тему:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ------------------------
# показать список лекций по теме
async def show_lectures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_name = update.message.text

    session = get_db_session()
    lectures_list = session.query(lectures).filter(lectures.c.topic == topic_name).all()
    session.close()

    if not lectures_list:
        await update.message.reply_text("Лекций по этой теме не найдено.")
        return

    keyboard = [[lec.name] for lec in lectures_list]
    context.user_data["current_topic"] = topic_name

    await update.message.reply_text(
        f"Лекции по теме '{topic_name}':",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ------------------------
# показать материалы лекции
async def show_lecture_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lecture_name = update.message.text

    session = get_db_session()
    lec = session.query(lectures).filter(lectures.c.name == lecture_name).first()
    session.close()

    if not lec:
        await update.message.reply_text("Не удалось найти лекцию.")
        return

    context.user_data["current_lecture"] = lec.id

    keyboard = [["🎧 Аудиозапись"], ["📄 Презентация"], ["📝 Конспект"]]

    await update.message.reply_text(
        f"Материалы для лекции '{lec.name}':",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ------------------------
# отправка файла или конспекта
async def send_material(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    lecture_id = context.user_data.get("current_lecture")

    if not lecture_id:
        await update.message.reply_text("Сначала выберите лекцию.")
        return

    session = get_db_session()
    lec = session.query(lectures).filter(lectures.c.id == lecture_id).first()
    session.close()

    if choice == "🎧 Аудиозапись" and lec.drive_audio_id:
        path = download_file_from_drive(lec.drive_audio_id, lec.name, "audio")
        if path:
            await update.message.reply_audio(open(path, "rb"))
            os.remove(path)
        else:
            await update.message.reply_text("Ошибка при скачивании аудио.")

    elif choice == "📄 Презентация" and lec.drive_slides_id:
        path = download_file_from_drive(lec.drive_slides_id, lec.name, "slides")
        if path:
            await update.message.reply_document(open(path, "rb"))
            os.remove(path)
        else:
            await update.message.reply_text("Ошибка при скачивании презентации.")

    elif choice == "📝 Конспект" and lec.summary_text:
        await update.message.reply_text(f"Конспект:\n\n{lec.summary_text}")
    else:
        await update.message.reply_text("Материал не найден.")


# ------------------------
# регистрация хендлеров
def register_handlers(app):
    app.add_handler(CommandHandler("lectures", show_topics))
    app.add_handler(MessageHandler(filters.Regex("^(?!/).*"), show_lectures))
    app.add_handler(MessageHandler(filters.Regex("^(?!/).*"), show_lecture_materials))
    app.add_handler(MessageHandler(filters.Regex("^(🎧 Аудиозапись|📄 Презентация|📝 Конспект)$"), send_material))