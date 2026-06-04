import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Railway provides MYSQLHOST, MYSQLUSER, etc.
    DB_HOST = os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('MYSQLUSER') or os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('MYSQLPASSWORD') or os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME') or 'mbstu_cp_ranking'
    DB_PORT = int(os.environ.get('MYSQLPORT') or 3306)
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Set to True in production with HTTPS
    SESSION_COOKIE_SECURE = False 
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
