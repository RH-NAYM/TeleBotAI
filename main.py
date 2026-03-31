from utils.config import API_TOKEN
from utils.patterns import mobile_pattern
import telebot
import re

# ==============================
# BOT INITIALIZATION
# ==============================
bot = telebot.TeleBot(API_TOKEN)


# ==============================
# COMMAND: START
# ==============================
@bot.message_handler(commands=["start"])
def start(msg):
    """Initialize bot interaction and greet the user."""
    grt = f"Hello {msg.from_user.first_name}, welcome to teleBotAI!"
    bot.send_message(msg.chat.id, grt)


# ==============================
# COMMAND: GATHER (ENTRY POINT)
# ==============================
@bot.message_handler(commands=["gather"])
def start_info_gathering(msg):
    """Start interactive user data collection flow."""
    bot.send_message(msg.chat.id, "Hi! What's your name?")
    bot.register_next_step_handler(msg, ask_age)


# ==============================
# NEXT STEP HANDLER FLOW
# ==============================

def ask_age(msg):
    """Collect user's name and ask for age."""
    name = msg.text.strip()
    bot.send_message(msg.chat.id, f"Nice to meet you, {name}! How old are you?")
    bot.register_next_step_handler(msg, ask_location, name=name)


def ask_location(msg, name):
    """Collect user's age and ask for location."""
    age = msg.text.strip()
    bot.send_message(msg.chat.id, f"Great {name}! You are {age} years old. Where are you from?")
    bot.register_next_step_handler(msg, ask_email, name=name, age=age)


def ask_email(msg, name, age):
    """Collect user's location and ask for email."""
    location = msg.text.strip()
    bot.send_message(msg.chat.id, f"Thanks {name}! What's your email?")
    bot.register_next_step_handler(msg, ask_phone, name=name, age=age, location=location)


def ask_phone(msg, name, age, location):
    """Collect user's email and ask for phone number."""
    email = msg.text.strip()
    bot.send_message(msg.chat.id, "Finally, please provide your phone number.")
    bot.register_next_step_handler(msg, summarize_info, name=name, age=age, location=location, email=email)


def summarize_info(msg, name, age, location, email):
    """Finalize and display all collected user information."""
    phone = msg.text.strip()

    bot.send_message(
        msg.chat.id,
        f"""
📋 USER INFORMATION

Name     : {name}
Age      : {age}
Location : {location}
Email    : {email}
Phone    : {phone}

✅ Data collection complete. Thank you!
"""
    )


# ==============================
# MOBILE NUMBER DETECTION
# ==============================
@bot.message_handler(func=lambda msg: msg.content_type == "text" and mobile_pattern.search(msg.text or ""))
def collect_mobile_number(msg):
    """Detect stacked mobile numbers (with optional '+') inside any text."""

    matches = mobile_pattern.findall(msg.text)

    # Clean extraction: join all matched parts safely
    numbers = []
    for match in matches:
        if isinstance(match, tuple):
            full_number = "".join([part for part in match if part])
        else:
            full_number = match

        if full_number:
            numbers.append(full_number)

    if numbers:
        bot.reply_to(msg, f"📞 Detected number(s): {', '.join(numbers)}")


# ==============================
# MEDIA HANDLER
# ==============================
@bot.message_handler(content_types=["photo", "audio", "video", "document"])
def handle_media(msg):
    """Handle incoming media files with appropriate responses."""

    responses = {
        "photo": "📷 Nice photo! Processing coming soon.",
        "audio": "🎧 Audio received. Processing not implemented yet.",
        "video": "🎥 Video received. Analysis feature coming soon.",
        "document": "📄 Document received. Parsing not supported yet."
    }

    bot.reply_to(msg, responses.get(msg.content_type, "Unsupported media type."))


# ==============================
# FALLBACK HANDLER (LAST PRIORITY)
# ==============================
@bot.message_handler(func=lambda msg: True)
def fallback(msg):
    """Handle all unmatched messages as a fallback response."""
    bot.reply_to(msg, "🤖 I didn't understand that. Use /help or /gather.")


# ==============================
# START BOT
# ==============================
bot.polling()
