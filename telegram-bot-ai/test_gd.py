# test_gd_download.py
import os
import tempfile
import requests

def download_from_drive(file_id: str, filename: str, file_type: str) -> str:
    """
    Скачивает файл с Google Drive и сохраняет с правильным расширением.
    """
    ext_map = {"audio": ".mp3", "slides": ".pdf", "other": ".bin"}
    ext = ext_map.get(file_type, ".bin")
    safe_name = filename.replace(" ", "_").replace("/", "_")
    tmp_path = os.path.join(tempfile.gettempdir(), f"{safe_name}{ext}")

    url = f"https://docs.google.com/uc?export=download&id={file_id}"
    print(f"[DriveTest] URL для скачивания: {url}")
    print(f"[DriveTest] Сохраняем как: {tmp_path}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_bytes = 0
        with open(tmp_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
                total_bytes += len(chunk)

        print(f"[DriveTest] Файл скачан, размер: {total_bytes / 1024:.2f} KB")
        return tmp_path

    except Exception as e:
        print(f"[DriveTest] Ошибка скачивания: {e}")
        return None

if __name__ == "__main__":
    # Вставьте сюда рабочий file_id с GD
    FILE_ID = "1RMmiHaCcYq9bbNVscp6c-3yqWjOdzR0q"
    FILENAME = "TestFile"
    FILE_TYPE = "slides"  # "audio" или "slides"

    downloaded_file = download_from_drive(FILE_ID, FILENAME, FILE_TYPE)
    if downloaded_file and os.path.exists(downloaded_file):
        print(f"[DriveTest] Проверка файла: {downloaded_file} существует ✅")
    else:
        print("[DriveTest] Файл не скачан ❌")