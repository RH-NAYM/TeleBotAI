from .utils.config import API_TOKEN
from telebot import TeleBot
from telebot.types import KeyboardButton,  ReplyKeyboardMarkup
import sqlite3

bot = TeleBot(token=API_TOKEN)


keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button = KeyboardButton(text="Send my Info", request_contact=True)
keyboard.add(button)


with sqlite3.connect("user.db") as connection:
    cursor = connection.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS users(
            id integer primary key,
            first_name text,
            last_name text,
            phone_number text
        );
    """
    cursor.execute(create_table_query)



@bot.message_handler(commands=["start"])
def send_welcome(msg):
    bot.send_message(msg.chat.id, text="Welcome to the Bot ! ", reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def contact(msg):
    # bot.send_message(msg.chat.id, text=f"{msg.contact}")
    with sqlite3.connect("user.db") as connection:
        cursor = connection.cursor()
        insert_data_query = """
            INSERT INTO users (id, first_name, last_name, phone_number)
            VALUES (?, ?, ?, ?)
        """

        data = (
            msg.contact.user_id,
            f"{msg.contact.first_name}",
            f"{msg.contact.last_name}",
            f"{msg.contact.phone_number}"
        )
        cursor.execute(insert_data_query, data)




bot.polling()
