import os
from telegram import ReplyKeyboardMarkup, KeyboardButton, InputFile
from ..db import get_db_session, lectures
from ..services.drive_service import download_file
from ..services.ai_client import ask_ai
from .audio import cmd_make_summary  # ✅ добавлено

# состояния меню
MAIN_MENU = "main"
CHOOSING_TOPIC = "choosing_topic"
CHOOSING_LECTURE = "choosing_lecture"

# ------------------------
# клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Лекционные материалы")],
            [KeyboardButton("Задать вопрос нейросети")],
            [KeyboardButton("Сделать краткий конспект")]
        ],
        resize_keyboard=True
    )

def get_topics_keyboard():
    session = get_db_session()
    topics = session.query(lectures.c.topic).distinct().all()
    session.close()
    keyboard = [[KeyboardButton(topic[0])] for topic in topics]
    keyboard.append([KeyboardButton("Главное меню")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_lectures_keyboard(topic_name):
    session = get_db_session()
    lectures_list = session.query(lectures).filter(lectures.c.topic == topic_name).all()
    session.close()
    keyboard = [[KeyboardButton(lec.name)] for lec in lectures_list]
    keyboard.append([KeyboardButton("Назад к темам"), KeyboardButton("Главное меню")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ai_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Выйти из чата")]], resize_keyboard=True)

# ------------------------
# отправка файлов
async def send_file(update, file_id, lecture_name, description, file_type="slides"):
    print(f"[send_file] Пользователь {update.effective_user.id} запросил {description} для лекции '{lecture_name}'")
    if not file_id:
        print(f"[send_file] ❌ Нет {description} для этой лекции")
        await update.message.reply_text(f"❌ Нет {description} для этой лекции.")
        return

    print(f"[send_file] Начало скачивания {description}, file_id={file_id}")
    file_path = download_file(file_id, lecture_name, file_type)
    if not file_path:
        print(f"[send_file] ❌ Не удалось скачать {description}")
        await update.message.reply_text(f"❌ Не удалось скачать {description}.")
        return

    print(f"[send_file] Скачано {file_path}, размер: {os.path.getsize(file_path)/1024:.2f} KB")
    try:
        if file_type == "audio":
            print(f"[send_file] Отправка аудио: {lecture_name}.mp3")
            with open(file_path, "rb") as f:
                await update.message.reply_audio(audio=InputFile(f, filename=f"{lecture_name}.mp3"))
        elif file_type == "slides":
            print(f"[send_file] Отправка PDF: {lecture_name}.pdf")
            with open(file_path, "rb") as f:
                await update.message.reply_document(document=InputFile(f, filename=f"{lecture_name}.pdf"))
        else:
            print(f"[send_file] Отправка бинарного файла: {lecture_name}")
            with open(file_path, "rb") as f:
                await update.message.reply_document(document=InputFile(f, filename=f"{lecture_name}.bin"))

        print(f"[send_file] Отправка завершена: {lecture_name}")
    except Exception as e:
        print(f"[send_file] ❌ Ошибка отправки {description}: {e}")
        await update.message.reply_text(f"❌ Ошибка отправки {description}: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[send_file] Файл удалён из памяти: {file_path}")

# ------------------------
# основной обработчик кнопок
async def button_handler(update, context):
    user_id = update.effective_user.id
    text = update.message.text
    print(f"[button_handler] Пользователь {user_id} отправил текст: {text}")
    state = context.user_data.get("state", MAIN_MENU)

    # === ЧАТ С НЕЙРОСЕТЬЮ ===
    if context.user_data.get("mode") == "ask_ai":
        print(f"[button_handler] Пользователь {user_id} находится в режиме AI")
        if text == "Выйти из чата":
            context.user_data["mode"] = None
            context.user_data["state"] = MAIN_MENU
            print(f"[button_handler] Пользователь {user_id} вышел из чата AI")
            await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())
            return

        if "ai_history" not in context.user_data:
            context.user_data["ai_history"] = []

        context.user_data["ai_history"].append({"role": "user", "content": text})
        thinking_msg = await update.message.reply_text("Думаю над ответом... 🤖", reply_markup=get_ai_keyboard())

        try:
            prompt = "\n".join(f"{m['role']}: {m['content']}" for m in context.user_data["ai_history"])
            answer = ask_ai(prompt)
            print(f"[button_handler] AI ответ для пользователя {user_id}: {answer[:100]}...")
            context.user_data["ai_history"].append({"role": "assistant", "content": answer})
            await update.message.reply_text(answer, reply_markup=get_ai_keyboard())
        except Exception as e:
            print(f"[button_handler] ❌ Ошибка при обращении к AI: {e}")
            await update.message.reply_text(f"❌ Ошибка при обращении к ИИ: {e}", reply_markup=get_ai_keyboard())
        finally:
            try:
                await thinking_msg.delete()
            except Exception:
                pass
        return

    # === ГЛАВНОЕ МЕНЮ ===
    if state == MAIN_MENU:
        print(f"[button_handler] Пользователь {user_id} в главном меню")
        if text == "Лекционные материалы":
            context.user_data["state"] = CHOOSING_TOPIC
            await update.message.reply_text("Выберите тему:", reply_markup=get_topics_keyboard())
        elif text == "Задать вопрос нейросети":
            context.user_data["mode"] = "ask_ai"
            context.user_data["ai_history"] = []
            await update.message.reply_text(
                "Ты вошёл в чат с нейросетью 🧠.\n"
                "Пиши сообщения подряд — я буду отвечать.\n"
                "Чтобы выйти, используй кнопку снизу.",
                reply_markup=get_ai_keyboard()
            )
        elif text == "Сделать краткий конспект":
            print(f"[button_handler] Пользователь {user_id} запустил аудио-конспект")
            return await cmd_make_summary(update, context)
        else:
            print(f"[button_handler] Пользователь {user_id} отправил неизвестную команду")
            await update.message.reply_text("Неизвестная команда. Выберите кнопку снизу 👇")
        return

    # === ВЫБОР ТЕМЫ ===
    if state == CHOOSING_TOPIC:
        print(f"[button_handler] Пользователь {user_id} выбрал тему: {text}")
        if text == "Главное меню":
            context.user_data["state"] = MAIN_MENU
            await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())
        else:
            context.user_data["state"] = CHOOSING_LECTURE
            context.user_data["topic_name"] = text
            await update.message.reply_text(
                f"Лекции по теме '{text}':",
                reply_markup=get_lectures_keyboard(text)
            )
        return

    # === ВЫБОР ЛЕКЦИИ ===
    if state == CHOOSING_LECTURE:
        print(f"[button_handler] Пользователь {user_id} выбрал лекцию: {text}")
        if text == "Назад к темам":
            context.user_data["state"] = CHOOSING_TOPIC
            await update.message.reply_text("Выберите тему:", reply_markup=get_topics_keyboard())
        elif text == "Главное меню":
            context.user_data["state"] = MAIN_MENU
            await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())
        else:
            topic_name = context.user_data.get("topic_name")
            print(f"[button_handler] Пользователь {user_id} ищет лекцию '{text}' в теме '{topic_name}'")
            session = get_db_session()
            lec = session.query(lectures).filter(
                lectures.c.topic == topic_name,
                lectures.c.name == text
            ).first()
            session.close()

            if not lec:
                print(f"[button_handler] ❌ Лекция не найдена: {text}")
                await update.message.reply_text("Лекция не найдена.")
                return

            if lec.drive_audio_id:
                print(f"[button_handler] Пользователь {user_id} запрашивает аудио {lec.name}")
                await send_file(update, lec.drive_audio_id, lec.name, "аудиозапись", file_type="audio")
            if lec.drive_slides_id:
                print(f"[button_handler] Пользователь {user_id} запрашивает презентацию {lec.name}")
                await send_file(update, lec.drive_slides_id, lec.name, "презентация", file_type="slides")
            if lec.summary_text:
                print(f"[button_handler] Отправка конспекта лекции {lec.name} пользователю {user_id}")
                await update.message.reply_text(f"📝 Конспект:\n{lec.summary_text}")