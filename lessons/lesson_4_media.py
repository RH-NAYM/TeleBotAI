# lesson_4_media.py
import telebot
from utils.config import API_TOKEN
from utils.patterns import mobile_pattern # Assumes this is a compiled re pattern

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=["photo", "video"])
def handle_media(msg):
    # Learning Point: content_types allows the bot to receive files
    bot.reply_to(msg, f"I received a {msg.content_type}!")

@bot.message_handler(func=lambda msg: mobile_pattern.search(msg.text or ""))
def detect_phone(msg):
    # Learning Point: 'func' allows custom logic to filter messages
    matches = mobile_pattern.findall(msg.text)
    bot.reply_to(msg, f"Found phone numbers: {matches}")

@bot.message_handler(func=lambda msg: True)
def fallback(msg):
    # Learning Point: This catches everything else (the 'Else' case)
    bot.send_message(msg.chat.id, "I'm not sure what to do with that.")

if __name__ == "__main__":
    print("Lesson 4 running...")
    bot.polling()
