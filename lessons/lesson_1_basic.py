# lesson_1_basic.py
import telebot
from utils.config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_welcome(msg):
    """
    Learning Point: Commands are defined in the 'commands' list.
    'msg' object contains user data like first_name and chat_id.
    """
    first_name = msg.from_user.first_name
    text = f"Hello {first_name}! I am Lesson 1 Bot. Use /start to see this."
    bot.send_message(msg.chat.id, text)

if __name__ == "__main__":
    print("Lesson 1 running...")
    bot.polling()
