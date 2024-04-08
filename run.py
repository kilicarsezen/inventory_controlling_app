# /inventory_controlling_app/run.py

from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env.development'))  # Adjust the file name based on environment

print("FLASK_ENV:", os.getenv('FLASK_ENV'))

from app import app  # Import the Flask app
print("DATABASE_URI:", os.getenv('DATABASE_URI'))
print("SQLAlchemy Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])


if __name__ == "__main__":
    app.run()
