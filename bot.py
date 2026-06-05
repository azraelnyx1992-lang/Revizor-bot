import requests
import time
import json
import os
import psycopg2

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 8248506377
offset = None

print("БОТ ЗАПУЩЕН ✅")

# ===== POSTGRESQL =====
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")
conn.commit()

last_message = {}


# ===== Функции работы с БД =====
def save_user(user_id, username, first_name):
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name
    """, (user_id, username, first_name))
    conn.commit()
    print("СОХРАНЕН:", user_id)


def remove_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    print("УДАЛЕН:", user_id)


def get_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


# ===== Основные функции бота =====
def send_menu(chat_id):
    keyboard = {
        "keyboard": [[{"text": "📌Закреп📌"}]],
        "resize_keyboard": True,
        "persistent": True
    }
    text = (
        "👋 <b>Привет</b>\n"
        "Ты написал оригинальному боту лучшей ДНР площадки "
        "💀<b>Донецкий Ревизор</b>💀\n"
        "Проверь оригинальность на сайте\n"
        "👉 Revizor.cc\n"
        "Для 100% результата введи сайт вручную в браузере.\n"
        "👇Нажми кнопку ниже чтобы получить доверенные магазины👇"
    )
    requests.post(URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    })


def send_post(chat_id):
    caption = (
        "😭 <b>Устал от фейков?</b> 😭\n"
        "❓Опять Мунтян предлагает в ЛС ровный шоп❓\n"
        "🚀 Пользуйся только проверенными магазинами 🚀\n"
        "💀 <b>Донецкий Ревизор</b> 💀\n"
        "🌐 Все настоящие контакты на сайте 🌐\n"
        "⚠️ Не ведитесь на фейков ⚠️\n"
        "📌 Revizor.cc 📌"
    )
    keyboard = {"inline_keyboard": [[{"text": "📎Revizor.cc📎", "url": "https://revizor.cc"}]]}
    requests.post(URL + "sendPhoto", data={
        "chat_id": chat_id,
        "photo": "https://i.ibb.co/21crjLB5/IMG-20260522-221607-203.jpg",
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    })


def broadcast_text(text):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    success = 0
    for user in users:
        user_id = user[0]
        try:
            resp = requests.post(URL + "sendMessage", data={
                "chat_id": user_id,
                "text": text,
                "parse_mode": "HTML"
            })
            data = resp.json()
            if not data.get("ok"):
                remove_user(user_id)
            else:
                success += 1
            time.sleep(0.3)
        except Exception as e:
            print("ОШИБКА РАССЫЛКИ:", e)
    return success


def broadcast_copy(from_chat_id, message_id):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    success = 0
    for user in users:
        user_id = user[0]
        try:
            resp = requests.post(URL + "copyMessage", data={
                "chat_id": user_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id
            })
            data = resp.json()
            if not data.get("ok"):
                remove_user(user_id)
            else:
                success += 1
            time.sleep(0.3)
        except Exception as e:
            print("ОШИБКА COPY:", e)
    return success


def send_text_to_user(user_id, text):
    resp = requests.post(URL + "sendMessage", data={
        "chat_id": user_id,
        "text": text,
        "parse_mode": "HTML"
    })
    return resp.json()


def copy_to_user(user_id, from_chat_id, message_id):
    resp = requests.post(URL + "copyMessage", data={
        "chat_id": user_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    })
    return resp.json()


def send_help(chat_id):
    text = (
        "🛠 <b>Админ-команды</b>\n\n"
        "/stats — показать количество пользователей\n"
        "/send текст — рассылка текста всем\n"
        "/dm user_id текст — отправка текстового сообщения одному пользователю\n"
        "/copyall — пересылка поста всем\n"
        "/copyto user_id — пересылка поста одному пользователю\n"
        "/help — показать это меню (только для админа)"
    )
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


# ===== Главный цикл =====
while True:
    try:
        response = requests.get(URL + "getUpdates", params={"offset": offset, "timeout": 30})
        data = response.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1
            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            chat_type = message["chat"]["type"]
            text = message.get("text", "")
            username = message["from"].get("username", "")
            first_name = message["from"].get("first_name", "")

            if chat_type != "private":
                continue

            now = time.time()
            if chat_id in last_message and now - last_message[chat_id] < 2:
                continue
            last_message[chat_id] = now

            save_user(chat_id, username, first_name)

            # Основные команды
            if text == "/start":
                send_menu(chat_id)
            elif text == "📌Закреп📌":
                send_post(chat_id)
            elif text == "/help" and chat_id == ADMIN_ID:
                send_help(chat_id)
            elif text == "/stats" and chat_id == ADMIN_ID:
                count = get_stats()
                requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": f"👥 Пользователей: {count}"})
            elif text.startswith("/send") and chat_id == ADMIN_ID:
                msg = text.replace("/send", "", 1).strip()
                if msg:
                    total = broadcast_text(msg)
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": f"✅ Текстовая рассылка отправлена: {total}"})
            elif text.startswith("/dm") and chat_id == ADMIN_ID:
                parts = text.split(" ", 2)
                if len(parts) < 3:
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": "❌ Формат: /dm user_id текст"})
                else:
                    target_id = parts[1]
                    msg = parts[2]
                    result = send_text_to_user(target_id, msg)
                    answer = "✅ Сообщение отправлено" if result.get("ok") else f"❌ Ошибка: {result}"
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": answer})
            elif text == "/copyall" and chat_id == ADMIN_ID:
                reply = message.get("reply_to_message")
                if not reply:
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": "❌ Ответьте командой /copyall на пост"})
                else:
                    from_chat_id = chat_id
                    message_id = reply["message_id"]
                    total = broadcast_copy(from_chat_id, message_id)
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": f"✅ Пост разослан: {total}"})
            elif text.startswith("/copyto") and chat_id == ADMIN_ID:
                reply = message.get("reply_to_message")
                parts = text.split()
                if not reply or len(parts) < 2:
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": "❌ Формат: ответьте на пост командой /copyto user_id"})
                else:
                    target_id = parts[1]
                    from_chat_id = chat_id
                    message_id = reply["message_id"]
                    result = copy_to_user(target_id, from_chat_id, message_id)
                    answer = "✅ Пост отправлен пользователю" if result.get("ok") else f"❌ Ошибка: {result}"
                    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": answer})

        time.sleep(1)

    except Exception as e:
        print("ОШИБКА:", e)
        time.sleep(5)
