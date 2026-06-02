import requests
import time
import json

TOKEN = "8899449640:AAFuYGws8VbMoNmTb8apSQCqZngSn73k_PY"

URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = None

print("БОТ ЗАПУЩЕН ✅")


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


# ОТПРАВКА САЙТА
def send_site(chat_id):

    requests.post(
        URL + "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "🌐 https://revizor.cc"
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

                chat_type = message["chat"]["type"]

                text = message.get("text", "")

                print("Сообщение:", text)

                # /start ТОЛЬКО В ЛС
                if text == "/start":

                    if chat_type == "private":

                        send_menu(chat_id)

                # КНОПКА МЕНЮ
                elif text == "📌Закреп📌":

                    # РАБОТАЕТ ТОЛЬКО В ЛС
                    if chat_type == "private":

                        send_site(chat_id)

        time.sleep(1)

    except Exception as e:

        print("ОШИБКА:", e)

        time.sleep(5)
