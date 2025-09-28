# bot/populate_db.py
# ------------------------
# Список всех лекций и file_id
# Просто замените FILE_ID_XXX на реальные file_id с Google Drive

lectures_data = [
    {
        "topic": "Программирование",
        "name": "Введение в Python",
        "drive_audio_id": "1IRuNsIEAYc--30Jmv_qzZOq59rpWV8M2",     # mp3 файл
        "drive_slides_id": "1RMmiHaCcYq9bbNVscp6c-3yqWjOdzR0q",   # pdf/pptx файл
        "summary_text": "Краткий конспект по введению в Python."
    },
    {
        "topic": "Программирование",
        "name": "Переменные и типы данных",
        "drive_audio_id": "1IRuNsIEAYc--30Jmv_qzZOq59rpWV8M2",
        "drive_slides_id": "1RMmiHaCcYq9bbNVscp6c-3yqWjOdzR0q",
        "summary_text": "Конспект о переменных и типах данных."
    },
    {
        "topic": "Базы данных",
        "name": "Введение в SQL",
        "drive_audio_id": "1IRuNsIEAYc--30Jmv_qzZOq59rpWV8M2",
        "drive_slides_id": "1RMmiHaCcYq9bbNVscp6c-3yqWjOdzR0q",
        "summary_text": "Конспект по SQL-запросам."
    },
    {
        "topic": "Базы данных",
        "name": "Таблицы и связи",
        "drive_audio_id": "1IRuNsIEAYc--30Jmv_qzZOq59rpWV8M2",
        "drive_slides_id": "1RMmiHaCcYq9bbNVscp6c-3yqWjOdzR0q",
        "summary_text": "Конспект про таблицы и связи между ними."
    }
]

# ------------------------
# Этот скрипт просто хранит данные.
# Для заполнения базы используйте populate_db_runner.py