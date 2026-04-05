# lesson_2_ui.py
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utils.config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

def get_main_keyboard():
    # Learning Point: KeyboardMarkup is a grid of buttons
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Alert Me", callback_data="btn1")
    btn2 = InlineKeyboardButton(text="Edit Message", callback_data="btn2")
    keyboard.add(btn1, btn2)
    return keyboard

@bot.message_handler(commands=["menu"])
def show_menu(msg):
    bot.send_message(msg.chat.id, "Choose an option:", reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Learning Point: callback_data identifies which button was clicked
    if call.data == "btn1":
        bot.answer_callback_query(call.id, "This is an alert!", show_alert=True)
    elif call.data == "btn2":
        bot.edit_message_text("The text has changed!", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print("Lesson 2 running...")
    bot.polling()
