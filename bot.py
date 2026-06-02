import requests
import time
import json

TOKEN = "8899449640:AAFuYGws8VbMoNmTb8apSQCqZngSn73k_PY"

URL = f"https://api.telegram.org/bot{TOKEN}/"

offset = None

print("БОТ ЗАПУЩЕН ✅")


# МЕНЮ (ТОЛЬКО В ЛС)
def send_menu(chat_id):

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "📌Закреп📌",
                "callback_data": "open_post"
            }
        ]]
    }

    requests.post(
        URL + "sendMessage",
        data={
            "chat_id": chat_id,
            "text": "👇 Нажми кнопку ниже 👇",
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

            # ОБЫЧНЫЕ СООБЩЕНИЯ
            if "message" in update:

                message = update["message"]

                chat_id = message["chat"]["id"]

                text = message.get("text", "")

                chat_type = message["chat"]["type"]

                user_id = message["from"]["id"]

                print("Сообщение:", text)

                # /start
                if text == "/start":

                    # ЕСЛИ ГРУППА/ЧАТ
                    if chat_type != "private":

                        # В ЧАТ БЕЗ КНОПКИ
                        requests.post(
                            URL + "sendMessage",
                            data={
                                "chat_id": chat_id,
                                "text": "📩 Проверь личные сообщения"
                            }
                        )

                        # КНОПКА ТОЛЬКО В ЛС
                        send_menu(user_id)

                    else:
                        # ЕСЛИ УЖЕ ЛС
                        send_menu(user_id)

            # НАЖАТИЕ INLINE КНОПКИ
            if "callback_query" in update:

                callback = update["callback_query"]

                data_btn = callback["data"]

                user_id = callback["from"]["id"]

                print("Нажата кнопка:", data_btn)

                # ОТПРАВКА ПОСТА В ЛС
                if data_btn == "open_post":

                    send_post(user_id)

                    # УБИРАЕМ ЧАСИК НА КНОПКЕ
                    requests.post(
                        URL + "answerCallbackQuery",
                        data={
                            "callback_query_id": callback["id"]
                        }
                    )

        time.sleep(1)

    except Exception as e:

        print("ОШИБКА:", e)

        time.sleep(5)
