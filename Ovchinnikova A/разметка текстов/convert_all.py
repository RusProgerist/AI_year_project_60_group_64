"""Сборка JSON-описаний из текстовых файлов корпуса.

Читает ``data/raw/*.txt`` и синхронизирует текст в парный ``*.json``.

ВАЖНО: скрипт неразрушающий. Он обновляет только поле ``text`` (и
подставляет ``id``/``title`` по умолчанию), но сохраняет уже заполненные
метаданные — ``author``, ``genre``, ``state``, ``source_url``, ``markers``.
Раньше скрипт перезаписывал JSON целиком и затирал эти поля заглушками.

Запускать можно из любого каталога: пути считаются от расположения файла.
"""

import json
import os
import sys
import tempfile

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")

# Поля, которые заполняются заглушками только если их ещё нет.
DEFAULTS = {
    "author": "Неизвестен",
    "genre": "",
    "state": "",
    "source_url": "",
    "markers": [],
}

# Служебные поля, которые всегда пересчитываются из имени файла.
DERIVED = {"id", "title"}


def build_entry(file_id, text, previous=None):
    """Собрать словарь записи, сохранив метаданные из ``previous``."""
    previous = previous or {}

    entry = {}
    entry["id"] = file_id
    entry["author"] = previous.get("author", DEFAULTS["author"])
    entry["title"] = previous.get("title") or file_id
    entry["genre"] = previous.get("genre", DEFAULTS["genre"])
    entry["state"] = previous.get("state", DEFAULTS["state"])
    entry["source_url"] = previous.get("source_url", DEFAULTS["source_url"])
    entry["text"] = text
    entry["markers"] = previous.get("markers", DEFAULTS["markers"])

    # Любые дополнительные поля, добавленные вручную, тоже сохраняем.
    for key, value in previous.items():
        if key not in entry:
            entry[key] = value

    return entry


def serialize(entry):
    """Каноническое представление записи (как писал исходный скрипт)."""
    return json.dumps(entry, ensure_ascii=False, indent=2)


def load_existing(json_path):
    """Прочитать существующий JSON; битый файл считаем отсутствующим."""
    if not os.path.isfile(json_path):
        return None
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def write_atomic(path, payload):
    """Записать файл целиком, не оставляя полузаписанного состояния."""
    directory = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(payload)
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def convert(raw_dir=RAW_DIR):
    """Синхронизировать все ``*.json`` с парными ``*.txt``.

    Возвращает кортеж ``(written, unchanged)``.
    """
    if not os.path.isdir(raw_dir):
        raise SystemExit(f"Нет каталога с текстами: {raw_dir}")

    written = unchanged = 0

    for filename in sorted(os.listdir(raw_dir)):
        if not filename.endswith(".txt"):
            continue

        file_id = filename[: -len(".txt")]
        txt_path = os.path.join(raw_dir, filename)
        json_path = os.path.join(raw_dir, f"{file_id}.json")

        with open(txt_path, encoding="utf-8") as f:
            text = f.read()

        previous = load_existing(json_path)
        payload = serialize(build_entry(file_id, text, previous))

        # Не трогаем файл, если содержимое не изменилось (идемпотентность).
        if os.path.isfile(json_path):
            with open(json_path, encoding="utf-8") as f:
                if f.read() == payload:
                    unchanged += 1
                    continue

        write_atomic(json_path, payload)
        written += 1
        print(f"Готово: {json_path}")

    return written, unchanged


def main():
    written, unchanged = convert()
    print(f"\nИтог: обновлено {written}, без изменений {unchanged}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
