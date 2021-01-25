from flask import Flask, request
from telegram.bot import Bot
from command import command_start
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
app = Flask(__name__)

users_dict = {}


@app.route('/', methods=["POST"])
def ex():
    data = request.get_json()
    if "message" in data:
        is_message(data["message"])
    if "callback_query" in data:
        is_CB(data["callback_query"])
    return "200"


def is_message(message: object):
    chat_id = message["from"]["id"]
    text = message["text"]
    if text == command_start:
        print(chat_id, "_________________________________")
        users_dict[chat_id] = Bot(TOKEN, chat_id)

    if chat_id in users_dict:
        users_dict[chat_id].last_message_id = None
        users_dict[chat_id].handle_input(text=text)


def is_CB(callback_query: object):
    cb_query_id = callback_query["id"]
    cb_data = callback_query["data"]
    chat_id = callback_query["from"]["id"]
    if cb_data is not None:
        users_dict[chat_id].answer_callback_query(callback_query_id=cb_query_id)
        users_dict[chat_id].handle_input(text=cb_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)