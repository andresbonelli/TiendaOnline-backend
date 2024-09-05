__all__ = ["MONGODB_URI",
           "logger",
           "SECRET_KEY",
           "REFRESH_KEY",
           "HOST_URL",
           "HOST_PORT",
           "FRONTEND_HOST",
           "FRONTEND_PORT",
           "MAIL_USERNAME",
           "MAIL_PASSWORD",
           "MAIL_FROM",
           "MAIL_PORT",
           "MAIL_SERVER",
           "APP_TITLE"]

import logging
import os

from dotenv import load_dotenv

# Cargamos nuestras variables de entorno
load_dotenv()

APP_TITLE = "Devlights Bootcamp 3.0 - Proyecto Final"

MONGODB_URI = os.getenv("MONGODB_CONNECTION_STRING")
if not MONGODB_URI:
    raise Exception("MongoDB connection string not found")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("Secret key not found")

REFRESH_KEY= os.getenv("REFRESH_KEY")
if not REFRESH_KEY:
    raise Exception("Refresh token secret key not found")

HOST_URL = os.getenv("HOST_URL", "localhost")
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "localhost")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))
HOST_PORT = int(os.getenv("HOST_PORT", "8000"))
MAIL_USERNAME=os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "")
MAIL_FROM=os.getenv("MAIL_FROM", "")
MAIL_PORT=int(os.getenv("MAIL_PORT", "1025"))
MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp")


logger = logging.getLogger("uvicorn")
# logger.setLevel(logging.DEBUG)

# Fixing a "bycript issue"
logging.getLogger("passlib").setLevel(logging.ERROR)