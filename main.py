from .config import API_TOKEN
import telebot


bot = telebot.TeleBot(API_TOKEN)













bot.polling()
