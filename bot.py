import requests
import time
import json
import sqlite3

TOKEN = "8899449640:AAFuYGws8VbMoNmTb8apSQCqZngSn73k_PY"

URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = None

print("БОТ ЗАПУЩЕН ✅")


# БАЗА ПОЛЬЗОВАТЕЛЕЙ
conn = sqlite3.connect("users.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()


# СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ
def save_user(user_id):

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()

    print("СОХРАНЕН:", user_id)


# МЕНЮ ТОЛЬКО В ЛС
def send_menu(chat_id):

    keyboard = {
        "keyboard": [
            [{"text": "📌Закреп📌"}]
        ],
        "resize_keyboard": True,
        "persistent": True
    }

    requests.post(
        URL + "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "👇 Кнопка меню снизу 👇",
            "reply_markup": json.dumps(keyboard)
        }
    )


# ПОСТ С ФОТО И КНОПКОЙ
def send_post(chat_id):

    caption = (
        "😭 Устал от фейков? 😭\n"
        "❓Опять Мунтян предлагает в ЛС ровный шоп❓\n"
        "🚀 Пользуйся только проверенными магазинами 🚀\n"
        "💀Донецкий Ревизор 💀\n"
        "🌐 Все настоящие контакты на сайте 🌐\n"
        "⚠️ Не ведитесь на фейков ⚠️\n"
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
            "reply_markup": json.dumps(keyboard)
        }
    )


# РАССЫЛКА
def broadcast_message(text):

    cursor.execute("SELECT user_id FROM users")

    users = cursor.fetchall()

    for user in users:

        user_id = user[0]

        try:

            requests.post(
                URL + "sendMessage",
                data={
                    "chat_id": user_id,
                    "text": text
                }
            )

            print("ОТПРАВЛЕНО:", user_id)

            time.sleep(0.3)

        except Exception as e:

            print("ОШИБКА:", e)


# ГЛАВНЫЙ ЦИКЛ
while True:

    try:

        response = requests.get(
            URL + "getUpdates",
            params={
                "offset": offset,
                "timeout": 5
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

                print("Сообщение:", text)

                # /start
                if text == "/start":

                    if chat_type == "private":

                        save_user(chat_id)

                        send_menu(chat_id)

                # КНОПКА
                elif text == "📌Закреп📌":

                    if chat_type == "private":

                        send_post(chat_id)

                # РАССЫЛКА ТОЛЬКО ДЛЯ ТЕБЯ
                elif text.startswith("/send"):

                    if chat_id == 8248506377:

                        msg = text.replace("/send", "").strip()

                        if msg:

                            broadcast_message(msg)

                            requests.post(
                                URL + "sendMessage",
                                data={
                                    "chat_id": chat_id,
                                    "text": "✅ Рассылка отправлена"
                                }
                            )

                # ЛЮБОЕ ДРУГОЕ СООБЩЕНИЕ
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
