# bot/handlers/audio.py
import os
import logging
import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

WAITING_AUDIO = 1

# ================== ВСПОМОГАТЕЛЬНЫЕ ==================

def ogg2wav(filename: str) -> str:
    """
    Перевод голосового сообщения из формата ogg в wav
    """
    logger.info(f"[AUDIO] Конвертация {filename} -> wav")
    new_filename = filename.replace('.ogg', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format="wav")
    return new_filename


def recognize_speech(wav_filename: str) -> str:
    """
    Распознавание речи через Google Speech Recognition
    """
    logger.info(f"[AUDIO] Распознаём речь из {wav_filename}")
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    text = recognizer.recognize_google(wav_audio, language="ru")
    logger.info(f"[AUDIO] Распознано: {text[:50]}...")
    return text

# ================== ОБРАБОТЧИКИ ==================

async def cmd_make_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("[AUDIO] cmd_make_summary вызван")
    await update.message.reply_text(
        "Отправь аудио или голосовое сообщение, и я сделаю краткий конспект 🎤"
    )
    return WAITING_AUDIO


async def receive_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[AUDIO] receive_audio вызван update={update}")

    file_id = None
    if update.message.voice:
        logger.info("[AUDIO] Обнаружено голосовое сообщение")
        file_id = update.message.voice.file_id
        ext = ".ogg"
    elif update.message.audio:
        logger.info("[AUDIO] Обнаружен аудиофайл")
        file_id = update.message.audio.file_id
        ext = ".mp3"
    else:
        logger.warning("[AUDIO] Сообщение не является аудио")
        await update.message.reply_text("Отправь именно голосовое или аудиофайл 🎧")
        return WAITING_AUDIO

    file = await context.bot.get_file(file_id)
    filename = f"temp_{file_id}{ext}"
    await file.download_to_drive(filename)
    logger.info(f"[AUDIO] Скачан файл {filename}")

    try:
        if ext == ".ogg":
            wav_filename = ogg2wav(filename)
        else:
            # если mp3 -> конвертим в wav
            wav_filename = filename.replace(ext, ".wav")
            audio = AudioSegment.from_file(filename)
            audio.export(wav_filename, format="wav")

        text = recognize_speech(wav_filename)
        response = f"🎤 Вот расшифровка вашего сообщения:\n\n{text}"
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"[AUDIO] Ошибка при обработке: {e}", exc_info=True)
        await update.message.reply_text("Не удалось распознать аудио 😢")

    finally:
        for f in (filename, locals().get("wav_filename")):
            if f and os.path.exists(f):
                os.remove(f)
                logger.info(f"[AUDIO] Файл {f} удалён")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("[AUDIO] cancel вызван")
    await update.message.reply_text("Операция отменена ❌")
    return ConversationHandler.END