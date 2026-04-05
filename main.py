import requests
import json
import time
from lessons.utils.config import API_TOKEN
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton,  ReplyKeyboardMarkup
from utils.tools import ToolsBot




__toolsBot__ = ToolsBot()


BOT_DATA = __toolsBot__.load_data("utils/data")


"""
BOT_DATA = {
  "users": [
    {
      "_id": "6259939132",
      "first_name": "Rakibul",
      "last_name": "Hasan",
      "phone_number": "8801638830165"
    }
  ],
  "urls": {
    "Malaysia": {
      "Daia-Face": "https://he.ngrok.app/status/face",
      "Daia-Main": "https://he.ngrok.app/status/daia"
    },
    "Bangladesh": {
      "BAT": {
        "BAT-Face": "https://hasb.nagadpulse.com/status/face",
        "BAT-Main": "https://hasb.nagadpulse.com/status/main",
        "BAT-Cluster-Upliftment": "https://hasb.nagadpulse.com/status/cluster_upliftment",
        "BAT-NLP": "https://hasb.nagadpulse.com/status/nlp"
      },
      "HE-Universe": {
        "HE-Universe-test-1": "test url test 1",
        "HE-Universe-test-2": "test url test 2",
        "HE-Universe-test-3": "test url test 3",
        "HE-Universe-test-4": "test url test 4"
      }
    }
  }
}
"""


bot = TeleBot(token=API_TOKEN)

def country():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Bangladesh", callback_data="Bangladesh")
    btn2 = InlineKeyboardButton(text="Malaysia", callback_data="Malaysia")
    keyboard.add(btn1, btn2)
    return keyboard




@bot.message_handler(commands=["check"])
def check_country(msg):
    first_name = msg.from_user.first_name
    bot.send_message(msg.chat.id, text=f"Hello {first_name}! Please Select Country.", reply_markup=country())
    # data = country()

    # print(data)



@bot.callback_query_handler(func=lambda data: True)
def check_country(data):
    if data.data in BOT_DATA["urls"]:
        __toolsBot__.monitor({"xxxxxxxxxxxxxxxxxxxxxxx": BOT_DATA["urls"][data.data]})
    else:
        print(data.data)































bot.polling()
