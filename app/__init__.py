# /inventory_controlling_app/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

app = Flask(__name__)
print("Environment:", os.getenv('FLASK_ENV', 'development'))
print("Database URI:", os.getenv('DATABASE_URI'))

if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig())
elif os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig())
elif os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object(TestingConfig())
else:
    app.config.from_object(DevelopmentConfig())  # Default to development if unsure

db = SQLAlchemy(app)

from app.models import models
migrate = Migrate(app, db)  # Initialize Flask-Migrate


# Rroute definitions and other app initializations go here

@app.route('/')
def hello_world():
    return 'Hello, World!'
