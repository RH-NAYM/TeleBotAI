import os
import re
import json
import logging
import traceback
import concurrent.futures
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import cv2
import numpy as np
import pandas as pd
import torch
import pytz
import commentjson
from PIL import Image, ImageOps
from aiohttp import ClientSession
from cryptography.fernet import Fernet

class ToolsBot:

    def monitor(self, data):
        print("~" * 100)
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("#" * 100)


    # Json Data Load Function
    def load_data(self, data_dir):
        json_data = {}

        def load_file(
            file,
        ):  # helper function to read and load all json files in the target dir
            file_name = os.path.splitext(file)[0]
            file_path = os.path.join(data_dir, file)
            with open(file_path, "r", encoding="utf-8") as data:
                # return file_name, json.load(data)
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
