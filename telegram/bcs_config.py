
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

NODE_URL = os.getenv("NODE_URL")
NODE_PASSWORD = os.getenv("NODE_PASSWORD")
NODE_USER = os.getenv("USER")
