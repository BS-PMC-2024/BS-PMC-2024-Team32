# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)
db_host = os.environ.get('DB_HOST', 'localhost')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:your_password@{db_host}/mathgenius'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'heythere'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
csrf = CSRFProtect(app)

from app import routes, models
