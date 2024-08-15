from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
TABLE_NAME = os.getenv("TABLE_NAME")
DB_NAME = os.getenv("DB_NAME")
