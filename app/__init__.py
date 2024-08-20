# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
import os
import logging
import subprocess

logging.basicConfig(filename='app.log', level=logging.DEBUG)
db_host = os.environ.get('DB_HOST', 'localhost')
app = Flask(__name__)
if os.environ.get('FLASK_ENV') == 'testing':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:your_password@{db_host}/mathgenius'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'heythere'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
csrf = CSRFProtect(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mathgeniussce@gmail.com'
app.config['MAIL_PASSWORD'] = 'tshy wyhc joys usho'  # We'll generate this in a moment
app.config['MAIL_DEFAULT_SENDER'] = 'mathgeniussce@gmail.com'
app.config['CONTACT_EMAIL'] = 'mathgeniussce@gmail.com' # Email to receive inquiries

mail = Mail(app)

from app import routes, models


def build_tailwind():
    subprocess.run([
        "tailwindcss",
        "-i", "app/static/css/tailwind.css",
        "-o", "app/static/css/tailwind.output.css",
        "--minify"
    ])

# Call this function before running the app
build_tailwind()

# Rest of your Flask app initialization...