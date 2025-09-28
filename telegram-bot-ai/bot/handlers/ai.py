# bot/handlers/ai.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from ..services.ai_client import ask_ai
from ..services.utils import markdown_to_html

# Клавиатура для выхода из чата
exit_kb = ReplyKeyboardMarkup([["⬅️ Выйти в меню"]], resize_keyboard=True)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диалога с нейросетью."""
    await update.message.reply_text(
        "Напиши свой вопрос, и я передам его нейросети.",
        reply_markup=exit_kb
    )
    context.user_data["ai_chat"] = True


async def ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений во время диалога с нейросетью."""
    user_text = update.message.text

    # Если пользователь решил выйти
    if user_text == "⬅️ Выйти в меню":
        context.user_data["ai_chat"] = False
        from .start import main_kb
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=main_kb
        )
        return

    # Проверяем, в режиме ли мы чата
    if not context.user_data.get("ai_chat"):
        await update.message.reply_text("Используй команду /ask, чтобы задать вопрос.")
        return

    # Сообщение "думаю..."
    waiting_msg = await update.message.reply_text("🤔 Думаю над ответом...")

    # Получаем ответ от модели
    answer = ask_ai(user_text)

    # Удаляем "думаю..."
    try:
        await waiting_msg.delete()
    except:
        pass

    # Отправляем ответ с поддержкой жирного/курсива/кода
    await update.message.reply_text(
        markdown_to_html(answer),
        parse_mode="HTML",
        reply_markup=exit_kb
    )