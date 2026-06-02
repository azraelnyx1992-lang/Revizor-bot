```python
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


# БАЗА ДАННЫХ
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


# АНТИСПАМ
last_message = {}


# СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ
def save_user(user_id, username, first_name):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username, first_name)
        VALUES (?, ?, ?)
        """,
        (user_id, username, first_name)
    )

    conn.commit()

    print("СОХРАНЕН:", user_id)


# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
def remove_user(user_id):

    cursor.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()

    print("УДАЛЕН:", user_id)


# СТАТИСТИКА
def get_stats():

    cursor.execute("SELECT COUNT(*) FROM users")

    count = cursor.fetchone()[0]

    return count


# МЕНЮ
def send_menu(chat_id):

    keyboard = {
        "keyboard": [
            [{"text": "📌Закреп📌"}]
        ],
        "resize_keyboard": True,
        "persistent": True
    }

    text = (
        "👋 <b>Привет</b>\n\n"
        "Ты написал оригинальному боту лучшей ДНР площадки "
        "💀<b>Донецкий Ревизор</b>💀\n\n"
        "Проверь оригинальность на сайте Revizor.cc\n"
        "Для 100% результата введи сайт вручную в браузере.\n\n"
        "👇Нажми кнопку ниже чтобы получить доверенные магазины👇"
    )

    requests.post(
        URL + "sendMessage",
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard)
        }
    )


# ПОСТ
def send_post(chat_id):

    caption = (
        "😭 <b>Устал от фейков?</b> 😭\n\n"
        "❓Опять Мунтян предлагает в ЛС ровный шоп❓\n\n"
        "🚀 Пользуйся только проверенными магазинами 🚀\n\n"
        "💀 <b>Донецкий Ревизор</b> 💀\n\n"
        "🌐 Все настоящие контакты на сайте 🌐\n\n"
        "⚠️ Не ведитесь на фейков ⚠️\n\n"
        "📌 Revizor.cc 📌"
    )

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "📎Revizor.cc📎",
                "url": "https://revizor.cc"
            }
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


# РАССЫЛКА
def broadcast_message(text):

    cursor.execute("SELECT user_id FROM users")

    users = cursor.fetchall()

    success = 0

    for user in users:

        user_id = user[0]

        try:

            response = requests.post(
                URL + "sendMessage",
                data={
                    "chat_id": user_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )

            data = response.json()

            if not data["ok"]:

                remove_user(user_id)

            else:

                success += 1

            print("ОТПРАВЛЕНО:", user_id)

            time.sleep(0.3)

        except Exception as e:

            print("ОШИБКА:", e)

    return success


# ГЛАВНЫЙ ЦИКЛ
while True:

    try:

        response = requests.get(
            URL + "getUpdates",
            params={
                "offset": offset,
                "timeout": 30
            }
        )

        data = response.json()

        for update in data["result"]:

            offset = update["update_id"] + 1

            if "message" in update:

                message = update["message"]

                chat_id = message["chat"]["id"]

                chat_type = message["chat"]["type"]

                text = message.get("text", "")

                username = message["from"].get("username", "")

                first_name = message["from"].get("first_name", "")

                print("СООБЩЕНИЕ:", text)

                # АНТИСПАМ
                now = time.time()

                if chat_id in last_message:

                    if now - last_message[chat_id] < 2:

                        continue

                last_message[chat_id] = now

                # /start
                if text == "/start":

                    if chat_type == "private":

                        save_user(
                            chat_id,
                            username,
                            first_name
                        )

                        send_menu(chat_id)

                # КНОПКА
                elif text == "📌Закреп📌":

                    if chat_type == "private":

                        send_post(chat_id)

                # РАССЫЛКА
                elif text.startswith("/send"):

                    if chat_id == ADMIN_ID:

                        msg = text.replace("/send", "").strip()

                        if msg:

                            total = broadcast_message(msg)

                            requests.post(
                                URL + "sendMessage",
                                data={
                                    "chat_id": chat_id,
                                    "text": f"✅ Рассылка отправлена: {total}",
                                }
                            )

                # СТАТИСТИКА
                elif text == "/stats":

                    if chat_id == ADMIN_ID:

                        count = get_stats()

                        requests.post(
                            URL + "sendMessage",
                            data={
                                "chat_id": chat_id,
                                "text": f"👥 Пользователей: {count}"
                            }
                        )

                # ВСЕ ОСТАЛЬНОЕ
                else:

                    requests.post(
                        URL + "sendMessage",
                        data={
                            "chat_id": chat_id,
                            "text": "Для начала работы нажмите /start"
                        }
                    )

        time.sleep(1)

    except Exception as e:

        print("ОШИБКА:", e)

        time.sleep(5)
```
