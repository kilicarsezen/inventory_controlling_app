# scripts/data_upload.py
import sys
import pandas as pd
from sqlalchemy import create_engine
sys.path.append('../')  # Adjust this path to ensure the app package can be found.
from app import create_app, db
from app.models import YourModel  # Replace with actual models you need.

class CSVHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_data(self):
        return pd.read_csv(self.filepath)

class AccessDBHandler:
    def __init__(self, db_path):
        self.db_path = db_path

    def read_data(self):
        # Assuming you're pulling a specific table from the Access DB
        return pd.read_sql_table('table_name', f"access+pyodbc://{self.db_path}")

def process_data(csv_data, access_data):
    # Implement your data processing logic here, possibly merging the two dataframes.
    # For example, a simple merge based on a common column:
    merged_data = pd.merge(csv_data, access_data, on='common_column', how='inner')
    return merged_data

def upload_data(data):
    app = create_app()
    with app.app_context():
        engine = create_engine(db.session.bind.engine.url)
        data.to_sql('your_table_name', con=engine, index=False, if_exists='append')

if __name__ == "__main__":
    csv_handler = CSVHandler('path/to/your.csv')
    access_handler = AccessDBHandler('path/to/your/access.db')

    csv_data = csv_handler.read_data()
    access_data = access_handler.read_data()

    processed_data = process_data(csv_data, access_data)
    upload_data(processed_data)
    print('Data processing and upload complete.')
