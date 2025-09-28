# bot/services/transcribe_service.py

import os
import speech_recognition as sr
from pydub import AudioSegment

def ogg2wav(filename: str) -> str:
    """
    Конвертация OGG → WAV
    """
    new_filename = filename.replace(".ogg", ".wav")
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format="wav")
    return new_filename

def transcribe_audio_local(path: str) -> str:
    """
    Транскрибация аудио через speech_recognition (Google Speech API).
    Поддерживает voice (.ogg) и audio (.mp3/.wav).
    """
    recognizer = sr.Recognizer()

    # Если пришёл OGG → конвертим в WAV
    if path.endswith(".ogg"):
        wav_path = ogg2wav(path)
    else:
        # если mp3/wav → в WAV
        wav_path = path.rsplit(".", 1)[0] + ".wav"
        audio = AudioSegment.from_file(path)
        audio.export(wav_path, format="wav")

    text = ""
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
    except Exception as e:
        text = f"Ошибка распознавания: {e}"

    # Удаляем временные файлы
    for f in [path, wav_path]:
        if os.path.exists(f):
            os.remove(f)

    return text