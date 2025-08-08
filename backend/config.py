import os
from dotenv import load_dotenv

load_dotenv()

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY and ENVIRONMENT == "production":
    print("⚠️  WARNING: OPENAI_API_KEY not set")

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://intellimail-90io.onrender.com/auth/callback")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
if JWT_SECRET_KEY == "your-secret-key-here" and ENVIRONMENT == "production":
    print("⚠️  WARNING: JWT_SECRET_KEY using default value")

# Gmail API Configuration
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000"
]

# Application Configuration
APP_NAME = "IntelliMail"
APP_VERSION = "1.0.0"
DEBUG = True

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
