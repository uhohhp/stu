# bot/services/drive_service.py
import os
import tempfile
import requests

def download_file(file_id: str, lecture_name: str, file_type: str) -> str:
    """
    Скачивает файл с Google Drive по file_id.
    Сохраняет во временную папку с правильным расширением.
    Возвращает путь к локальному файлу.
    """
    if not file_id:
        return None

    url = f"https://docs.google.com/uc?export=download&id={file_id}"

    ext_map = {"audio": ".mp3", "slides": ".pdf", "other": ".bin"}
    ext = ext_map.get(file_type, ".bin")

    safe_name = lecture_name.replace(" ", "_").replace("/", "_")
    tmp_path = os.path.join(tempfile.gettempdir(), f"{safe_name}{ext}")

    try:
        print(f"[DriveService] Скачивание {file_type}, lecture_name={lecture_name}, file_id={file_id}")
        print(f"[DriveService] URL для скачивания: {url}")
        print(f"[DriveService] Файл будет сохранен как: {tmp_path}")

        r = requests.get(url, stream=True)
        r.raise_for_status()

        total = int(r.headers.get('content-length', 0))
        downloaded = 0

        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    percent = downloaded / total * 100
                    print(f"\r[DriveService] Загрузка {lecture_name}: {percent:.0f}%", end="")
        print()
        print(f"[DriveService] Файл скачан, размер: {os.path.getsize(tmp_path)/1024:.2f} KB")

        return tmp_path
    except Exception as e:
        print(f"[DriveService] Ошибка скачивания {file_id}: {e}")
        return None