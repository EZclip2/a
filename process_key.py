import os
import re
import sys
import base64
import hashlib
import string
import random
import requests
from datetime import datetime

# ════════════════════════════════════════════════════════════════
#  КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════

RESULTS_REPO = "EZclip2/Results_repository"

MIN_CHECKSUM = 12544
MAX_CHECKSUM = 16384

CODING_MAP = {
    "а": "X7k", "б": "9pL", "в": "qW3", "г": "MtR", "д": "5Bf",
    "е": "aBc", "ё": "7jY", "ж": "ZxN", "з": "4wQ", "и": "gH2",
    "й": "UvP", "к": "Qa9", "л": "0sT", "м": "pLm", "н": "1hG",
    "о": "QwE", "п": "2yU", "р": "As8", "с": "3tK", "т": "rTy",
    "у": "Zc6", "ф": "BnM", "х": "vB6", "ц": "8nX", "ч": "PoI",
    "ш": "9Kj", "щ": "wEr", "ъ": "Fg2", "ы": "LkJ", "ь": "8rT",
    "э": "ZaQ", "ю": "7dF", "я": "Ws5",
    "А": "xYz", "Б": "9L3", "В": "QRt", "Г": "m8N", "Д": "6bV",
    "Е": "AB9", "Ё": "3Jk", "Ж": "zXc", "З": "6pO", "И": "gHi",
    "Й": "uV4", "К": "qAw", "Л": "8Nm", "М": "PlK", "Н": "7kJ",
    "О": "qWe", "П": "8T7", "Р": "aSd", "С": "9Mf", "Т": "RtY",
    "У": "zC8", "Ф": "bCv", "Х": "VbN", "Ц": "5N2", "Ч": "pOi",
    "Ш": "3Lk", "Щ": "We6", "Ъ": "FgH", "Ы": "lK9", "Ь": "2rT",
    "Э": "zAq", "Ю": "1Dw", "Я": "WsX",
    "a": "P7a", "b": "5kB", "c": "Df2", "d": "Stv", "e": "8Mc",
    "f": "GhJ", "g": "hJ3", "h": "2wQ", "i": "KlM", "j": "Op6",
    "k": "1zX", "l": "6Xc", "m": "Bn9", "n": "2qW", "o": "nF7",
    "p": "CvB", "q": "5Tg", "r": "AbC", "s": "fG4", "t": "4nM",
    "u": "IjK", "v": "jK7", "w": "1rT", "x": "LmN", "y": "Vb8",
    "z": "3sD",
    "A": "p9A", "B": "7kB", "C": "dFc", "D": "sTv", "E": "0mE",
    "F": "gHf", "G": "hJg", "H": "4Wh", "I": "kLi", "J": "oPj",
    "K": "5zK", "L": "8xL", "M": "bNm", "N": "6qN", "O": "xYo",
    "P": "cVp", "Q": "9tQ", "R": "aBr", "S": "fGs", "T": "8vT",
    "U": "iJu", "V": "jKv", "W": "1eW", "X": "lMx", "Y": "vBy",
    "Z": "7sZ",
    "0": "z0X", "1": "O1x", "2": "T2m", "3": "h3N",
    "4": "F4r", "5": "v5K", "6": "S6r", "7": "E7w",
    "8": "i8Q", "9": "N9p",
    " ": "spC", ",": "cmT", ".": "Dt9", "!": "ExK", "?": "qtM",
    "-": "DsR", "`": "Gr6", "~": "tLp", "@": "At2", "#": "HsV",
    "$": "DlR", "%": "Pc4", "^": "CrT", "&": "Am7", "_": "UnD",
    "+": "pLs", "=": "Eq3", "{": "LbR", "}": "Rb5", "[": "LsQ",
    "]": "Rs8", ";": "ScM", "'": "Ap6"
}

NUMBER_MAP = {
    "0": "qW8eR0t", "1": "aS2Df1g", "2": "Zx5Cv2B",
    "3": "pO9iU3y", "4": "Lk7jH4g", "5": "mN4bV5c",
    "6": "Qa3zA6w", "7": "eD1cR7f", "8": "yH6nU8j",
    "9": "oL2pK9i"
}

NUMBER_MAP2 = {
    "0": "tR3wQ8k", "1": "gF5hJ1x", "2": "bV7nM2p",
    "3": "yU4cX3s", "4": "hG9dL4z", "5": "cN6fB5w",
    "6": "wA8kP6m", "7": "fC2jT7n", "8": "jH5gR8v",
    "9": "iK3eS9q"
}

DECODE_MAP = {v: k for k, v in CODING_MAP.items()}
NUMBER_DECODE_MAP = {v: k for k, v in NUMBER_MAP.items()}
NUMBER_DECODE_MAP2 = {v: k for k, v in NUMBER_MAP2.items()}

SEPARATOR = CODING_MAP[' ']  # "spC"


# ════════════════════════════════════════════════════════════════
#  КОДИРОВАНИЕ / ДЕКОДИРОВАНИЕ
# ════════════════════════════════════════════════════════════════

def encode_text(text):
    encoded = ""
    for char in text:
        if char in CODING_MAP:
            encoded += CODING_MAP[char]
        else:
            return None
    return encoded


def decode_text(encoded):
    decoded = ""
    i = 0
    while i < len(encoded):
        chunk = encoded[i:i+3]
        if chunk in DECODE_MAP:
            decoded += DECODE_MAP[chunk]
        else:
            decoded += "?"
        i += 3
    return decoded


def encode_number(number):
    encoded = ""
    for digit in str(number):
        if digit in NUMBER_MAP:
            encoded += NUMBER_MAP[digit]
    return encoded


def decode_number(encoded_str):
    decoded = ""
    i = 0
    while i < len(encoded_str):
        chunk = encoded_str[i:i+7]
        if chunk in NUMBER_DECODE_MAP:
            decoded += NUMBER_DECODE_MAP[chunk]
        else:
            return None
        i += 7
    try:
        return int(decoded) if decoded else None
    except ValueError:
        return None


def decode_number_user(encoded_str):
    decoded = ""
    i = 0
    while i < len(encoded_str):
        chunk = encoded_str[i:i+7]
        if chunk in NUMBER_DECODE_MAP2:
            decoded += NUMBER_DECODE_MAP2[chunk]
        else:
            return None
        i += 7
    try:
        return int(decoded) if decoded else None
    except ValueError:
        return None


# ════════════════════════════════════════════════════════════════
#  ЗАПИСЬ РЕЗУЛЬТАТА В Results_repository
# ════════════════════════════════════════════════════════════════

def write_result(uuid, status, days, token):
    if not uuid or not token:
        return

    content = f"{uuid};{status};{days}"
    encoded = base64.b64encode(content.encode()).decode()
    filename = f"{uuid}.txt"
    api_url = f"https://api.github.com/repos/{RESULTS_REPO}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    sha = None
    r = requests.get(api_url, headers=headers, timeout=10)
    if r.ok:
        sha = r.json().get("sha")

    payload = {
        "message": f"Result {filename}",
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha

    requests.put(api_url, headers=headers, json=payload, timeout=10).raise_for_status()


def fail(uuid, token):
    write_result(uuid, 0, 0, token)


# ════════════════════════════════════════════════════════════════
#  ОСНОВНАЯ ЛОГИКА ПРОВЕРКИ
# ════════════════════════════════════════════════════════════════

def main():
    full_key = os.environ.get("INPUT_KEY", "").strip()
    device_uuid = os.environ.get("INPUT_UUID", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    keys_token = os.environ.get("KEYS_TOKEN", "")
    results_token = os.environ.get("RESULTS_TOKEN", "")

    if not full_key or not device_uuid:
        if device_uuid:
            fail(device_uuid, results_token)
        return

    # --- Парсинг ключа: password:encoded_number ---
    if ":" not in full_key:
        fail(device_uuid, results_token)
        return

    colon_idx = full_key.rfind(":")
    password = full_key[:colon_idx]
    encoded_num_user = full_key[colon_idx + 1:]

    if not password or not encoded_num_user:
        fail(device_uuid, results_token)
        return

    # Декодируем номер ключа (NUMBER_MAP2)
    key_number = decode_number_user(encoded_num_user)
    if not key_number:
        fail(device_uuid, results_token)
        return

    # --- Проверка длины пароля ---
    if not (64 <= len(password) <= 72):
        fail(device_uuid, results_token)
        return

    # --- Проверка checksum ---
    numbers_in_password = re.findall(r'\d+', password)
    checksum = sum(int(n) for n in numbers_in_password)

    if not (MIN_CHECKSUM <= checksum <= MAX_CHECKSUM):
        fail(device_uuid, results_token)
        return

    # --- Проверка кодируемости пароля ---
    encoded_password = encode_text(password)
    if not encoded_password:
        fail(device_uuid, results_token)
        return

    # --- Поиск файла ключа в репозитории ---
    headers = {
        "Authorization": f"token {keys_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    api_base = f"https://api.github.com/repos/{repo}/contents"

    try:
        r = requests.get(f"{api_base}/", headers=headers, timeout=15)
        r.raise_for_status()
        files = r.json()
    except Exception:
        fail(device_uuid, results_token)
        return

    # Ищем файл по номеру (NUMBER_MAP)
    encoded_num = encode_number(key_number)
    file_info = None

    for f in files:
        name = f["name"]
        if not name.endswith(".txt"):
            continue
        clean = name[2:] if name.startswith("0.") else name
        if clean.startswith(f"{encoded_num}."):
            file_info = f
            break

    if not file_info:
        fail(device_uuid, results_token)
        return

    # Заморожен?
    if file_info["name"].startswith("0."):
        fail(device_uuid, results_token)
        return

    # --- Скачивание и SHA1 ---
    try:
        r = requests.get(file_info["download_url"], timeout=10)
        content = r.content
        blob = f"blob {len(content)}\0".encode() + content
        if hashlib.sha1(blob).hexdigest() != file_info.get("sha", ""):
            fail(device_uuid, results_token)
            return
    except Exception:
        fail(device_uuid, results_token)
        return

    # --- Парсинг содержимого ---
    # Формат: encoded_password + SEPARATOR + encoded_date + [SEPARATOR + encoded_uuid] + tail_char
    content_str = content.decode("utf-8").strip()
    content_str = content_str[:-1]  # убираем tail_char

    parts = content_str.split(SEPARATOR)

    if len(parts) < 2:
        fail(device_uuid, results_token)
        return

    stored_encoded_password = parts[0]
    stored_encoded_date = parts[1]
    stored_encoded_uuid = parts[2] if len(parts) >= 3 else None

    # --- Проверка пароля ---
    if stored_encoded_password != encoded_password:
        fail(device_uuid, results_token)
        return

    # --- Checksum из имени файла ---
    filename_parts = file_info["name"].replace(".txt", "").split(".")
    if len(filename_parts) >= 3:
        stored_checksum = decode_number(filename_parts[2])
        if stored_checksum is not None and stored_checksum != checksum:
            fail(device_uuid, results_token)
            return

    # --- Дата истечения ---
    expiry_str = decode_text(stored_encoded_date)

    try:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
    except ValueError:
        fail(device_uuid, results_token)
        return

    now = datetime.utcnow()
    if now.date() > expiry_date.date():
        fail(device_uuid, results_token)
        return

    # --- Привязка устройства ---
    stored_uuid = decode_text(stored_encoded_uuid) if stored_encoded_uuid else None

    if stored_uuid:
        if stored_uuid != device_uuid:
            fail(device_uuid, results_token)
            return
    else:
        encoded_uuid = encode_text(device_uuid)
        if encoded_uuid:
            tail_char = random.choice(string.ascii_letters + string.digits)
            new_content = content_str + SEPARATOR + encoded_uuid + tail_char
            try:
                requests.put(
                    f"{api_base}/{file_info['name']}",
                    headers=headers,
                    timeout=10,
                    json={
                        "message": f"Bind device #{key_number}",
                        "content": base64.b64encode(new_content.encode()).decode(),
                        "sha": file_info["sha"],
                    },
                ).raise_for_status()
            except Exception:
                fail(device_uuid, results_token)
                return

    # --- Успех ---
    days_left = (expiry_date.date() - now.date()).days
    write_result(device_uuid, 1, days_left, results_token)


if __name__ == "__main__":
    main()