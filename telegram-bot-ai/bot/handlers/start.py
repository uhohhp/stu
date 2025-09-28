from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Лекционные материалы")],
            [KeyboardButton("Задать вопрос нейросети")],
            [KeyboardButton("Сделать краткий конспект")]
        ],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    context.user_data["state"] = "main"