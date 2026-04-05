from utils.config import API_TOKEN
from telebot import TeleBot

bot = TeleBot(token=API_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(msg):
    bot.send_message(msg.chat.id, text="Welcome to the Bot!")


@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_members(msg):
    for i in msg.new_chat_members:
        txt = f"👋 User {msg.from_user.first_name}, welcome to the group 🎊🎊🎊"
        bot.send_message(msg.chat.id, text=txt)



def check_admin(chat_id, user_id):
    admins = bot.get_chat_administrators(chat_id=chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
        else:
            False

@bot.message_handler(func=lambda msg: msg.text == "pin")
def pin_msg(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    if check_admin(chat_id=chat_id, user_id=user_id):
        if msg.reply_to_message:
            bot.pin_chat_message(chat_id=chat_id, message_id=msg.reply_to_message.message_id)
            bot.reply_to(msg.reply_to_message, text="The message is pinned successfully")

        else:
            bot.reply_to(msg, text="Please reply to the message you want to pin.")
    else:
        bot.send_message(msg.chat.id, text="Only admins can pin messages")

bot.polling()
