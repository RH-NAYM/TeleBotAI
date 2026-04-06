import asyncio
import traceback
import uuid
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

# 🔥 GLOBAL CALLBACK MAP (fix for BUTTON_DATA_INVALID)
CALLBACK_MAP = {}


# -----------------------
# Async runner (SAFE)
# -----------------------
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            return new_loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


# -----------------------
# Helpers
# -----------------------
def get_data_by_path(data, path_list):
    try:
        current = data
        for key in path_list:
            if key not in current:
                return None
            current = current[key]
        return current
    except Exception:
        traceback.print_exc()
        return None


def create_buttons(current_level, path=None, max_buttons_per_row=3):
    try:
        path = path or []
        rows, temp_row = [], []

        for key in current_level.keys():
            cb_id = str(uuid.uuid4())[:8]
            CALLBACK_MAP[cb_id] = path + [key]

            temp_row.append(
                InlineKeyboardButton(
                    text=key,
                    callback_data=cb_id
                )
            )

            if len(temp_row) == max_buttons_per_row:
                rows.append(temp_row)
                temp_row = []

        if temp_row:
            rows.append(temp_row)

        # Back + Home buttons
        if path:
            back_id = str(uuid.uuid4())[:8]
            CALLBACK_MAP[back_id] = path[:-1]

            root_id = str(uuid.uuid4())[:8]
            CALLBACK_MAP[root_id] = []

            rows.append([
                InlineKeyboardButton("⬅️ Back", callback_data=back_id),
                InlineKeyboardButton("🏠 Main Menu", callback_data=root_id)
            ])
        else:
            root_id = str(uuid.uuid4())[:8]
            CALLBACK_MAP[root_id] = []

            rows.append([
                InlineKeyboardButton("🏠 Main Menu", callback_data=root_id)
            ])

        return InlineKeyboardMarkup(rows)

    except Exception:
        traceback.print_exc()


# -----------------------
# USER CHECK
# -----------------------
def check_user(user_id, chat_id):
    try:
        if __toolsBot__.is_registered_user(user_id):
            return True

        try:
            with open(__toolsBot__.UNREGISTERED_FILE, "r", encoding="utf-8") as f:
                unreg_users = [str(u["_id"]) for u in json.load(f)]
        except Exception:
            unreg_users = []

        if str(user_id) not in unreg_users:
            kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            kb.add(KeyboardButton("📲 Share Contact", request_contact=True))

            bot.send_message(
                chat_id,
                "❌ You are not registered! Please share your contact.",
                reply_markup=kb
            )
            return False
        else:
            bot.send_message(chat_id, "⏳ Waiting for admin approval.")
            return False

    except Exception:
        traceback.print_exc()


# -----------------------
# /check
# -----------------------
@bot.message_handler(commands=["check"])
def check_command(msg):
    if not check_user(msg.from_user.id, msg.chat.id):
        return

    markup = create_buttons(BOT_DATA["urls"])

    bot.send_message(
        msg.chat.id,
        "📊 *AI Service Dashboard*\nSelect a system:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


# -----------------------
# Callback handler
# -----------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if not check_user(call.from_user.id, call.message.chat.id):
            bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return

        data = call.data

        # 🔥 FIXED: use mapping instead of raw string
        if data not in CALLBACK_MAP:
            bot.answer_callback_query(call.id, "⚠️ Button expired. Please retry.", show_alert=True)
            return

        path = CALLBACK_MAP[data]

        current = get_data_by_path(BOT_DATA["urls"], path) if path else BOT_DATA["urls"]

        if current is None:
            bot.answer_callback_query(call.id, "Invalid path", show_alert=True)
            return

        # -----------------------
        # FINAL NODE (API CALL)
        # -----------------------
        if isinstance(current, str):

            if not current.strip():
                bot.answer_callback_query(call.id, "No endpoint configured", show_alert=True)
                return

            bot.answer_callback_query(call.id, f"Checking {path[-1]}...")

            result = run_async(
                __checker__.run_check(path[-1], current, path)
            )

            bot.send_message(
                call.message.chat.id,
                result,
                parse_mode="Markdown"
            )

            parent_path = path[:-1]
            parent_data = get_data_by_path(BOT_DATA["urls"], parent_path) if parent_path else BOT_DATA["urls"]

            bot.send_message(
                call.message.chat.id,
                f"🔁 *Continue Checking* | {' > '.join(parent_path) if parent_path else 'Dashboard'}",
                reply_markup=create_buttons(parent_data, parent_path),
                parse_mode="Markdown"
            )
            return

        # -----------------------
        # NAVIGATION NODE
        # -----------------------
        bot.send_message(
            call.message.chat.id,
            f"📂 {' > '.join(path) if path else 'Dashboard'}",
            reply_markup=create_buttons(current, path),
            parse_mode="Markdown"
        )

    except Exception:
        traceback.print_exc()


# -----------------------
# CONTACT HANDLER
# -----------------------
@bot.message_handler(content_types=['contact'])
def handle_contact(msg):
    try:
        user_id = msg.from_user.id
        contact = msg.contact

        __toolsBot__.add_unregistered_user(
            user_id,
            msg.from_user.first_name,
            msg.from_user.last_name or "",
            contact.phone_number
        )

        bot.send_message(
            msg.chat.id,
            "✅ Info received. Wait for admin approval."
        )

    except Exception:
        traceback.print_exc()


# -----------------------
# FALLBACK
# -----------------------
@bot.message_handler(func=lambda m: True)
def handle_messages(msg):
    check_user(msg.from_user.id, msg.chat.id)


# -----------------------
# RUN
# -----------------------
bot.polling()
