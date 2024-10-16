from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
SECRET_KEY = os.environ.get("SECRET_KEY")

EMAIL_FROM = os.environ.get("EMAIL_ADDRESS_FROM")
EMAIL_PASS = os.environ.get("EMAIL_PASSWORD")

SERVER_HOSTNAME = os.environ.get("SERVER_HOSTNAME")
