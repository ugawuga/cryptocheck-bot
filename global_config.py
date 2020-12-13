import os
from dotenv import load_dotenv

load_dotenv()

DB_API_PORT = os.getenv("DB_API_PORT")
DB_API_URL = os.getenv("DB_API_URL")
BCS_API_URL = os.getenv("BCS_API_URL")
