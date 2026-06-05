import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Print loaded env variables (Redacted)
print(f"DEBUG STARTUP: DB_HOST={os.environ.get('DB_HOST')}, DB_PORT={os.environ.get('DB_PORT')}, RENDER={os.environ.get('RENDER')}")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Priority: DB_HOST > MYSQLHOST > localhost
    DB_HOST = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST') or 'localhost'
    
    # Priority: DB_PORT > MYSQLPORT > 3306
    _port = os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT') or '3306'
    DB_PORT = int(_port)
    
    DB_USER = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE') or 'mbstu_cp_ranking'
    # Aiven requires SSL
    DB_SSL_REQUIRED = os.environ.get('DB_SSL_REQUIRED', 'False').lower() == 'true' or os.environ.get('VERCEL') is not None or os.environ.get('RENDER') is not None
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Set to True in production with HTTPS
    SESSION_COOKIE_SECURE = False 
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
