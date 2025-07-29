# axisbot — Python библиотека для ботов AxisMessenger

## Установка

```bash
pip install axisbot  # (после публикации на PyPI)
```

## Быстрый старт (polling)

```python
from axisbot import AxisBot

bot = AxisBot("AxisBotABCDE:12345", base_url="https://your-messenger.com/api")

@bot.on_message
def handle_message(update):
    if "ping" in update.text:
        bot.send_message(update.chat_id, "pong!")
    else:
        bot.send_message(update.chat_id, f"Вы написали: {update.text}")

bot.polling()
```

## Webhook-режим

```python
from axisbot import AxisBot
from flask import Flask, request

bot = AxisBot("AxisBotABCDE:12345", base_url="https://your-messenger.com/api")
app = Flask(__name__)

@bot.on_message
def handle(update):
    bot.send_message(update.chat_id, "Webhook OK!")

@app.route("/webhook", methods=["POST"])
def webhook():
    bot.webhook_handler(request.json)
    return "ok"

if __name__ == "__main__":
    bot.set_webhook("https://your-server.com/webhook")
    app.run(port=8080)
```

## Кнопки и вложения

```python
from axisbot import AxisBot, MessageButton

bot = AxisBot("AxisBotABCDE:12345", base_url="https://your-messenger.com/api")

@bot.on_message
def handle(update):
    if update.text == "/buttons":
        buttons = [[MessageButton("Кнопка 1", "btn1"), MessageButton("Кнопка 2", "btn2")]]
        bot.send_message(update.chat_id, "Выберите:", buttons=buttons)
    elif update.button_data:
        bot.send_message(update.chat_id, f"Вы нажали: {update.button_data}")
    elif update.attachments:
        for att in update.attachments:
            bot.send_message(update.chat_id, f"Получен файл: {att.filename}")

bot.polling()
```

## Документация

- [Полная документация по AxisMessenger Bot API](../docs/bot_api.md)

## Лицензия
MIT 