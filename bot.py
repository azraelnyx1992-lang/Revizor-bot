import requests
import time
import json

TOKEN = "8899449640:AAFuYGws8VbMoNmTb8apSQCqZngSn73k_PY"

URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = None

print("БОТ ЗАПУЩЕН ✅")


# МЕНЮ
def send_menu(chat_id):

    keyboard = {
        "keyboard": [
            [{"text": "📌Закреп📌"}]
        ],
        "resize_keyboard": True
    }

    requests.post(
        URL + "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "👇 Нужно нажать кнопку снизу 👇",
            "reply_markup": json.dumps(keyboard)
        }
    )


# ПОСТ
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

                text = message.get("text", "")

                print("Сообщение:", text)

                # /start
                if text == "/start":

                    send_menu(chat_id)

                # КНОПКА
                elif text == "📌Закреп📌":

                    send_post(chat_id)

        time.sleep(1)

    except Exception as e:

        print("ОШИБКА:", e)

        time.sleep(5)
