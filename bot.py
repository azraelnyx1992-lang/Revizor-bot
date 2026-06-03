import requests
import time
import json
import sqlite3
import os

TOKEN = os.getenv("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = None
ADMIN_ID = 8248506377

print("БОТ ЗАПУЩЕН ✅")

# DB
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")
conn.commit()

last_message = {}

# СОХРАНЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
def save_user(user_id, username, first_name):
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username, first_name))
    conn.commit()


def remove_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()


def get_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.post(URL + "sendMessage", data=data)


def send_menu(chat_id):
    keyboard = {
        "keyboard": [[{"text": "📌Закреп📌"}]],
        "resize_keyboard": True
    }

    text = (
        "👋 <b>Привет</b>\n"
        "💀 <b>Донецкий Ревизор</b> 💀\n"
        "👉 Revizor.cc"
    )

    send_message(chat_id, text, keyboard)


def send_post(chat_id):
    caption = (
        "💀 <b>Донецкий Ревизор</b> 💀\n"
        "🌐 Revizor.cc"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "📎 Открыть сайт", "url": "https://revizor.cc"}
        ]]
    }

    requests.post(
        URL + "sendPhoto",
        data={
            "chat_id": chat_id,
            "photo": "https://i.ibb.co/21crjLB5/IMG-20260522-221607-203.jpg",
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard)
        }
    )


def broadcast(text):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    success = 0

    for (user_id,) in users:
        try:
            r = requests.post(URL + "sendMessage", data={
                "chat_id": user_id,
                "text": text,
                "parse_mode": "HTML"
            })

            if r.json().get("ok"):
                success += 1
            else:
                remove_user(user_id)

            time.sleep(0.3)

        except:
            pass

    return success


print("БОТ РАБОТАЕТ...")

while True:
    try:
        response = requests.get(
            URL + "getUpdates",
            params={"offset": offset, "timeout": 30}
        )

        data = response.json()

        for update in data["result"]:
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            msg = update["message"]

            chat_id = msg["chat"]["id"]
            chat_type = msg["chat"]["type"]
            text = msg.get("text", "")
            username = msg["from"].get("username", "")
            first_name = msg["from"].get("first_name", "")

            # антиспам
            now = time.time()
            if chat_id in last_message and now - last_message[chat_id] < 1.5:
                continue
            last_message[chat_id] = now

            # 🔥 ВАЖНО: сохраняем ВСЕХ пользователей при любом сообщении
            if chat_type == "private":
                save_user(chat_id, username, first_name)

            # /start
            if text == "/start" and chat_type == "private":
                send_menu(chat_id)

            # кнопка
            elif text == "📌Закреп📌" and chat_type == "private":
                send_post(chat_id)

            # админ рассылка
            elif text.startswith("/send") and chat_id == ADMIN_ID:
                msg_text = text.replace("/send", "").strip()
                if msg_text:
                    count = broadcast(msg_text)
                    send_message(chat_id, f"✅ Отправлено: {count}")

            # статистика
            elif text == "/stats" and chat_id == ADMIN_ID:
                send_message(chat_id, f"👥 Пользователей: {get_stats()}")

            # ❌ НИКАКОГО ELSE СПАМА НЕТ

        time.sleep(1)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)
