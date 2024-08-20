from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
import subprocess


# Load environment variables first
load_dotenv()

if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Apply configurations from Config class
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# CSRF protection
csrf = CSRFProtect(app)

# Mail setup
mail = Mail(app)

def build_tailwind():
    subprocess.run([
        "tailwindcss",
        "-i", "app/static/css/tailwind.css",
        "-o", "app/static/css/tailwind.output.css",
        "--minify"
    ])

# Build tailwind on app start
build_tailwind()


from app import models
from app import routes