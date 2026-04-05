from utils.config import API_TOKEN
from utils.patterns import mobile_pattern
import telebot
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


bot = telebot.TeleBot(API_TOKEN)













bot.polling()
