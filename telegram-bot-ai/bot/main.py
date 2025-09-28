# bot/main.py
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from .db import init_db
from .handlers.callbacks import button_handler
from .handlers.start import start  # если есть стартовое сообщение
from .handlers.audio import cmd_make_summary, receive_audio, cancel, WAITING_AUDIO
from .handlers.ai import ask_command  # чтобы работала команда /ask


# ================= ЛОГИРОВАНИЕ =================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= СОЗДАНИЕ ПРИЛОЖЕНИЯ =================
def build_app():
    from .config import TG_TOKEN
    if not TG_TOKEN:
        raise RuntimeError("TG_TOKEN не найден в .env")

    app = ApplicationBuilder().token(TG_TOKEN).build()

    # ====== Команды ======
    if 'start' in globals():
        app.add_handler(CommandHandler("start", start))

    # Вопрос напрямую в нейросеть
    app.add_handler(CommandHandler("ask", ask_command))

    # Конспект из аудио
    audio_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("summary", cmd_make_summary)],
        states={
            WAITING_AUDIO: [
                MessageHandler(filters.AUDIO | filters.VOICE, receive_audio),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(audio_conv_handler)

    # ====== Текстовые кнопки (callback) ======
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    return app

# ================= ЗАПУСК =================
def main():
    init_db()  # Инициализация базы
    app = build_app()
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()