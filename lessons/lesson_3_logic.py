# lesson_3_logic.py
import telebot
from utils.config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["gather"])
def start_flow(msg):
    # Learning Point: register_next_step_handler 'waits' for the next user message
    sent_msg = bot.send_message(msg.chat.id, "Step 1: What is your name?")
    bot.register_next_step_handler(sent_msg, process_name)

def process_name(msg):
    name = msg.text
    sent_msg = bot.send_message(msg.chat.id, f"Hi {name}, how old are you?")
    # Pass 'name' forward to the next function
    bot.register_next_step_handler(sent_msg, process_age, name=name)

def process_age(msg, name):
    age = msg.text
    bot.send_message(msg.chat.id, f"Summary: {name} is {age} years old.")

if __name__ == "__main__":
    print("Lesson 3 running...")
    bot.polling()
