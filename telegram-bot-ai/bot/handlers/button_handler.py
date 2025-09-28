from ..db import get_db_session, lectures

# Для AI
from ..services.ai_client import ask_ai

async def button_handler(update, context):
    text = update.message.text

    # Режим AI
    if context.user_data.get("mode") == "ask_ai":
        await update.message.reply_text("Думаю над ответом... 🤖")
        answer = ask_ai(text)
        await update.message.reply_text(answer)
        context.user_data["mode"] = None
        return

    # Лекции
    if text == "Лекционные материалы":
        await show_topics(update, context)
        return

    elif text == "Задать вопрос нейросети":
        context.user_data["mode"] = "ask_ai"
        await update.message.reply_text("Задай свой вопрос 📝")
        return

    elif text == "Сделать краткий конспект":
        await update.message.reply_text("Отправь аудио, и я сделаю конспект 🎤")
        return

    await update.message.reply_text("Неизвестная команда. Выбери кнопку снизу 👇")


# ------------------------
# функции для показа тем и лекций через ReplyKeyboard
async def show_topics(update, context):
    session = get_db_session()
    topics = session.query(lectures.c.topic).distinct().all()
    session.close()

    # создаём ReplyKeyboard с темами
    keyboard = [[topic[0]] for topic in topics]
    keyboard.append(["Назад"])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите тему:", reply_markup=markup)

    # сохраняем состояние пользователя
    context.user_data["state"] = "choosing_topic"


async def show_lectures(update, context):
    topic_name = update.message.text
    session = get_db_session()
    lectures_list = session.query(lectures).filter(lectures.c.topic == topic_name).all()
    session.close()

    if not lectures_list:
        await update.message.reply_text("Лекции не найдены.")
        return

    keyboard = [[lec.name] for lec in lectures_list]
    keyboard.append(["Назад"])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"Лекции по теме '{topic_name}':", reply_markup=markup)

    context.user_data["state"] = "choosing_lecture"
    context.user_data["topic_name"] = topic_name


async def show_lecture_materials(update, context):
    lecture_name = update.message.text
    topic_name = context.user_data.get("topic_name")
    session = get_db_session()
    lec = session.query(lectures).filter(
        lectures.c.topic == topic_name, lectures.c.name == lecture_name
    ).first()
    session.close()

    if not lec:
        await update.message.reply_text("Лекция не найдена.")
        return

    text = f"Материалы для лекции '{lec.name}':\n"
    if lec.drive_audio_id:
        text += f"🎧 Аудиозапись: https://drive.google.com/uc?id={lec.drive_audio_id}&export=download\n"
    if lec.drive_slides_id:
        text += f"📄 Презентация: https://drive.google.com/uc?id={lec.drive_slides_id}&export=download\n"
    if lec.summary_text:
        text += f"📝 Конспект:\n{lec.summary_text}\n"

    await update.message.reply_text(text)

    # После показа материалов возвращаем меню тем
    await show_topics(update, context)


# ------------------------
# Обновляем button_handler, чтобы переходить между состояниями
async def button_handler(update, context):
    text = update.message.text

    # Режим AI
    if context.user_data.get("mode") == "ask_ai":
        await update.message.reply_text("Думаю над ответом... 🤖")
        answer = ask_ai(text)
        await update.message.reply_text(answer)
        context.user_data["mode"] = None
        return

    state = context.user_data.get("state")
    if state == "choosing_topic":
        if text == "Назад":
            context.user_data["state"] = None
            return await start(update, context)
        await show_lectures(update, context)
        return
    elif state == "choosing_lecture":
        if text == "Назад":
            context.user_data["state"] = "choosing_topic"
            await show_topics(update, context)
            return
        await show_lecture_materials(update, context)
        return

    # Основное меню
    if text == "Лекционные материалы":
        await show_topics(update, context)
    elif text == "Задать вопрос нейросети":
        context.user_data["mode"] = "ask_ai"
        await update.message.reply_text("Задай свой вопрос 📝")
    elif text == "Сделать краткий конспект":
        await update.message.reply_text("Отправь аудио, и я сделаю конспект 🎤")
    else:
        await update.message.reply_text("Неизвестная команда. Выбери кнопку снизу 👇")