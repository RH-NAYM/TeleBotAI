import asyncio
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from lessons.utils.config import API_TOKEN
from utils.tools import ToolsBot
from utils.check import ServiceChecker

bot = TeleBot(API_TOKEN)
__toolsBot__ = ToolsBot()
__checker__ = ServiceChecker()
BOT_DATA = __toolsBot__.load_data("utils/data")


# -----------------------
# Helper functions
# -----------------------
def get_data_by_path(data, path_list):
    current = data
    for key in path_list:
        current = current.get(key, {})
    return current


def create_buttons(current_level, path=None, max_buttons_per_row=3):
    path = path or []
    rows, temp_row = [], []

    for key in current_level.keys():
        temp_row.append(InlineKeyboardButton(text=key, callback_data="|".join(path + [key])))
        if len(temp_row) == max_buttons_per_row:
            rows.append(temp_row)
            temp_row = []
    if temp_row:
        rows.append(temp_row)

    # Back + Main Menu always in same row
    if path:
        back_btn = InlineKeyboardButton("⬅️ Back", callback_data="|".join(path[:-1]) or "root")
        main_btn = InlineKeyboardButton("🏠 Main Menu", callback_data="root")
        rows.append([back_btn, main_btn])
    else:
        rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="root")])

    return InlineKeyboardMarkup(rows)


# -----------------------
# /check command
# -----------------------
@bot.message_handler(commands=["check"])
def check_command(msg):
    markup = create_buttons(BOT_DATA["urls"])
    bot.send_message(msg.chat.id, "📊 *AI Service Dashboard*\nSelect a system to check:",
                     reply_markup=markup, parse_mode="Markdown")


# -----------------------
# Callback handler
# -----------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    path = [] if data == "root" else data.split("|")
    current = get_data_by_path(BOT_DATA["urls"], path) if path else BOT_DATA["urls"]

    # Final URL → run check synchronously using asyncio.run
    if isinstance(current, str):
        bot.answer_callback_query(call.id, f"⏳ Checking {path[-1]}...", show_alert=True)

        # Run async checker synchronously to avoid "no running loop"
        import asyncio
        result = asyncio.run(__checker__.run_check(name=path[-1], url=current, path=path))
        bot.send_message(call.message.chat.id, result, parse_mode="Markdown")

        # Show parent menu automatically
        parent_path = path[:-1]
        parent_data = get_data_by_path(BOT_DATA["urls"], parent_path) if parent_path else BOT_DATA["urls"]
        bot.send_message(
            call.message.chat.id,
            f"🔁 *Continue Checking* | 📂 {' > '.join(parent_path) if parent_path else 'Dashboard'}",
            reply_markup=create_buttons(parent_data, parent_path),
            parse_mode="Markdown",
        )
        return

    # Intermediate menu → show submenu
    bot.send_message(
        call.message.chat.id,
        f"📂 {' > '.join(path) if path else 'Dashboard'}",
        reply_markup=create_buttons(current, path),
        parse_mode="Markdown",
    )


# -----------------------
# Run bot
# -----------------------
bot.polling()
