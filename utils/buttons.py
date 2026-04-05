
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup






def country():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Bangladesh", callback_data="btn1")
    btn2 = InlineKeyboardButton(text="Malaysia", callback_data="btn2")
    keyboard.add(btn1, btn2)
    return keyboard





