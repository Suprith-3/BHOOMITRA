import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:

    # ------------------------------------------------
    # Flask Security
    # ------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    GEMINI_API_KEY = os.getenv("AIzaSyCHWhTofVBRtkAbx1pmeqxXo44Nk2389bU")
    # ------------------------------------------------
    # Database Configuration
    # ------------------------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "agri_platform.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------
    # Mail Configuration (OTP Verification)
    # ------------------------------------------------
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("GMAIL_EMAIL")
    MAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

    # ------------------------------------------------
    # API Keys
    # ------------------------------------------------
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    #GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")

    # ------------------------------------------------
    # File Upload Configuration
    # ------------------------------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
