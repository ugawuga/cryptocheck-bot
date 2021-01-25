
import os
from dotenv import load_dotenv

load_dotenv()

NODE_URL = os.getenv("NODE_URL")
NODE_USER = os.getenv("NODE_USER")
NODE_PASSWORD = os.getenv("NODE_PASSWORD")
