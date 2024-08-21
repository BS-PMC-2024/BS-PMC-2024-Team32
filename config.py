import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback_secret_key')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
    DB_NAME = os.getenv('DB_NAME', 'mathgenius')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'mathgeniussce@gmail.com')
    CONTACT_EMAIL = 'mathgeniussce@gmail.com'
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
