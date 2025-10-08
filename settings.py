import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("PASSWORD")
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "Bulk Mailer")
