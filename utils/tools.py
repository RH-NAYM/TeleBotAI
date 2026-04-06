# utils/tools.py
import os
import json
import concurrent.futures
import commentjson
from cryptography.fernet import Fernet
import random

class ToolsBot:
    UNREGISTERED_FILE = "utils/data/unregistered_users.json"

    def __init__(self):
        # Ensure unregistered file exists
        if not os.path.exists(self.UNREGISTERED_FILE):
            with open(self.UNREGISTERED_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def monitor(self, data):
        print("~" * 100)
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("#" * 100)

    # JSON Data Load Function
    def load_data(self, data_dir):
        json_data = {}

        def load_file(file):
            file_name = os.path.splitext(file)[0]
            file_path = os.path.join(data_dir, file)
            with open(file_path, "r", encoding="utf-8") as data:
                return file_name, commentjson.load(data)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            json_data.update(
                dict(
                    executor.map(
                        load_file,
                        [f for f in os.listdir(data_dir) if f.endswith(".json")],
                    )
                )
            )
        return json_data

    def decrypt_key(self):
        """Decrypt encrypted_data.bin into a dict (not a file)."""
        try:
            with open("projectBAT/BAT_Main/utils/secure/secret.key", "rb") as key_file:
                key = key_file.read()
        except FileNotFoundError:
            raise RuntimeError("Missing encryption key file: secret.key")

        cipher = Fernet(key)

        try:
            with open("projectBAT/BAT_Main/utils/secure/encrypted_data.bin", "rb") as f:
                encrypted_data = f.read()
        except FileNotFoundError:
            raise RuntimeError("Missing encrypted data file: encrypted_data.bin")

        try:
            decrypted_data = cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise RuntimeError(f"Failed to decrypt service account: {e}")

    # -------------------------
    # USER VALIDATION METHODS
    # -------------------------
    def is_registered_user(self, user_id):
        """Check if the Telegram user is registered."""
        BOT_DATA = self.load_data("utils/data")
        users = BOT_DATA.get("users", [])
        for u in users:
            if str(user_id) == str(u.get("_id")):
                return True
        return False

    def add_unregistered_user(self, user_id, first_name=None, last_name=None, phone_number=None):
        """Add unregistered user to JSON file."""
        try:
            with open(self.UNREGISTERED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

        # Check if already exists
        for u in data:
            if str(u.get("_id")) == str(user_id):
                return

        # Add new entry
        new_user = {
            "_id": str(user_id),
            "first_name": first_name or "",
            "last_name": last_name or "",
            "phone_number": phone_number or ""
        }
        data.append(new_user)

        with open(self.UNREGISTERED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    IGNORE_MESSAGES = [
        "I don't talk to strangers 🤖",
        "Unauthorized access detected ❌",
        "You shall not pass 🛑",
        "Access denied. Move along 🚷",
        "I only respond to authorized humans 👽",
        "Hmm… I don't know you 😶",
        "This is not your bot. Bye 👋",
        "Unauthorized user alert! ⚠️",
        "Access refused. Contact admin 🔒",
        "I’m ignoring you. Seriously 🤖"
    ]

    def random_ignore_msg(self):
        """Return a random ignore message for unregistered users."""
        return random.choice(self.IGNORE_MESSAGES)
