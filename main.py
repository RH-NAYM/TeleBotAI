# main.py
import asyncio
import traceback
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import json
from lessons.utils.config import API_TOKEN
from utils.tools import ToolsBot
from utils.check import ServiceChecker

bot = TeleBot(API_TOKEN)
__toolsBot__ = ToolsBot()
__checker__ = ServiceChecker()
BOT_DATA = __toolsBot__.load_data("utils/data")

# -----------------------
# Helpers
# -----------------------
def get_data_by_path(data, path_list):
    try:
        current = data
        for key in path_list:
            print(key,path_list)
            current = current.get(key, {})
        return current
    except Exception as e:
        traceback.print_exc()

def create_buttons(current_level, path=None, max_buttons_per_row=3):
    try:
        path = path or []
        rows, temp_row = [], []

        for key in current_level.keys():
            temp_row.append(InlineKeyboardButton(text=key, callback_data="|".join(path + [key])))
            if len(temp_row) == max_buttons_per_row:
                rows.append(temp_row)
                temp_row = []
        if temp_row:
            rows.append(temp_row)

        if path:
            back_btn = InlineKeyboardButton("⬅️ Back", callback_data="|".join(path[:-1]) or "root")
            main_btn = InlineKeyboardButton("🏠 Main Menu", callback_data="root")
            rows.append([back_btn, main_btn])
        else:
            rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="root")])

        return InlineKeyboardMarkup(rows)
    except Exception as e:
        traceback.print_exc()

# -----------------------
# USER CHECK
# -----------------------
def check_user(user_id, chat_id):
    try:
        # Approved users
        if __toolsBot__.is_registered_user(user_id):
            return True

        # Unregistered or pending
        # Check if already in unregistered
        try:
            with open(__toolsBot__.UNREGISTERED_FILE, "r", encoding="utf-8") as f:
                unreg_users = [str(u["_id"]) for u in json.load(f)]
        except Exception:
            unreg_users = []

        if str(user_id) not in unreg_users:
            # Ask to share contact
            kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            kb.add(KeyboardButton("📲 Share Contact", request_contact=True))
            bot.send_message(
                chat_id,
                "❌ You are not registered! Please share your contact with the bot to register.",
                reply_markup=kb
            )
            return False
        else:
            # Already shared but pending approval
            bot.send_message(chat_id, "✅ Your info has been received. Please wait for admin approval.", reply_markup=None)
            return False
    except Exception as e:
        traceback.print_exc()

# -----------------------
# /check command
# -----------------------
@bot.message_handler(commands=["check"])
def check_command(msg):
    try:
        user_id = msg.from_user.id
        if not check_user(user_id, msg.chat.id):
            return

        markup = create_buttons(BOT_DATA["urls"])
        bot.send_message(
            msg.chat.id,
            "📊 *AI Service Dashboard*\nSelect a system to check:",
            reply_markup=markup,
            parse_mode="Markdown",
        )
    except Exception as e:
        traceback.print_exc()

# -----------------------
# CONTACT SHARING
# -----------------------
@bot.message_handler(content_types=['contact'])
def handle_contact(msg):
    try:
        user_id = msg.from_user.id
        contact = msg.contact
        first_name = msg.from_user.first_name
        last_name = msg.from_user.last_name or ""
        phone_number = contact.phone_number

        # Save to unregistered users
        __toolsBot__.add_unregistered_user(user_id, first_name, last_name, phone_number)
        bot.send_message(
            msg.chat.id,
            f"✅ Thank you {first_name}! Your info has been saved.\nPlease wait for admin approval.",
            reply_markup=None
        )
    except Exception as e:
        traceback.print_exc()

# -----------------------
# Catch-all message for enforcing registration
# -----------------------
@bot.message_handler(func=lambda m: True)
def handle_messages(msg):
    try:
        user_id = msg.from_user.id
        check_user(user_id, msg.chat.id)
    except Exception as e:
        traceback.print_exc()

# -----------------------
# Callback handler
# -----------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        user_id = call.from_user.id
        if not check_user(user_id, call.message.chat.id):
            # Stop unapproved users from interacting
            bot.answer_callback_query(
                call.id,
                "❌ You are not authorized. Please share your contact first.",
                show_alert=True
            )
            return

        data = call.data
        path = [] if data == "root" else data.split("|")
        current = get_data_by_path(BOT_DATA["urls"], path) if path else BOT_DATA["urls"]

        if isinstance(current, str):
            bot.answer_callback_query(call.id, f"⏳ Checking {path[-1]}...", show_alert=True)
            result = asyncio.run(__checker__.run_check(name=path[-1], url=current, path=path))
            bot.send_message(call.message.chat.id, result, parse_mode="Markdown")

            parent_path = path[:-1]
            parent_data = get_data_by_path(BOT_DATA["urls"], parent_path) if parent_path else BOT_DATA["urls"]

            bot.send_message(
                call.message.chat.id,
                f"🔁 *Continue Checking* | 📂 {' > '.join(parent_path) if parent_path else 'Dashboard'}",
                reply_markup=create_buttons(parent_data, parent_path),
                parse_mode="Markdown",
            )
            return

        bot.send_message(
            call.message.chat.id,
            f"📂 {' > '.join(path) if path else 'Dashboard'}",
            reply_markup=create_buttons(current, path),
            parse_mode="Markdown",
        )
    except Exception as e:
        traceback.print_exc()

# -----------------------
# Run bot
# -----------------------
bot.polling()
