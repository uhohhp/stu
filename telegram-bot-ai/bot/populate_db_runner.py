# bot/populate_db_runner.py
from bot.db import get_db_session, lectures
from bot.populate_db import lectures_data


def populate():
    session = get_db_session()

    # Удаляем старые записи
    session.execute(lectures.delete())

    # Добавляем новые записи из lectures_data
    session.execute(lectures.insert(), lectures_data)

    session.commit()
    session.close()
    print("База лекций успешно заполнена!")


if __name__ == "__main__":
    populate()