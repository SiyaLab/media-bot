import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Telegram Bot API key
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# MySQL database credentials
# url: 'mysql://root:zxaS68MF@localhost:3306/ThengaDB_Dev',
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
