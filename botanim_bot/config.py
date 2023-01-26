import os

from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SQLITE_DB_FILE = "db.sqlite3"
DATE_FORMAT = "%d.%m.%Y"
VOTE_ELEMENTS_COUNT = 3

ALL_BOOKS_CALLBACK_PATTERN = "all_books_"
VOTE_BOOKS_CALLBACK_PATTERN = "vote_"
