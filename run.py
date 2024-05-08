# /inventory_controlling_app/run.py

from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env.development'))  # Adjust the file name based on environment

from app import app  # Import the Flask app

if __name__ == "__main__":
    app.run()
