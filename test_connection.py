from sqlalchemy import create_engine

# Adjusted connection string to match the working snippet
engine = create_engine("mssql+pyodbc://localhost/Inventory_APP_DB?driver=ODBC Driver 17 for SQL Server")
connection = engine.connect()
print("Connection successful")
connection.close()

