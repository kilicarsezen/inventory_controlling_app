# scripts/data_upload.py
import sys
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import urllib
import numpy as np
sys.path.append('../')  # Adjust this path to ensure the app package can be found.
pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.3f' % x)
# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (which is the root of your Flask app)
parent_dir = os.path.dirname(script_dir)
# Load the .env file from the parent directory
load_dotenv(os.path.join(parent_dir, '.env.development'))

from app import app, db
# from app.models import YourModel  # Replace with actual models you need.
from urllib.parse import quote_plus

# to-do:
# add material description to sap md data
# add artificial material number to JP codes
# download open orders, supply, forecast from sap
# add data upload script for above tables



class CSVHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_data(self, filenmae):
        return pd.read_csv(os.path.join(self.filepath, filenmae), sep='\t')
    
class XLSXHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_data(self, filenmae):
        return pd.read_excel(os.path.join(self.filepath, filenmae))
    
class AccessDBHandler:
    def __init__(self, db_path):
        # Construct the connection string for pyodbc
        params = urllib.parse.quote_plus(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path}")
        # Create the SQLAlchemy engine
        self.engine = create_engine(f"access+pyodbc:///?odbc_connect={params}")

    def read_data(self, code_correction):
        # Use the engine to read a table into a DataFrame
        with self.engine.connect() as conn:
            Code_Numbers_All_master_test = pd.read_sql(f"SELECT * FROM Component", conn)
            StorageLocation = pd.read_sql("SELECT * FROM StorageLocation", conn) 
            Sourcer = pd.read_sql("SELECT * FROM Sourcer", conn) 
            Location = pd.read_sql("SELECT * FROM Location", conn) 
            FACTS = pd.read_sql("SELECT * FROM FACTS", conn) 
            FACTS = FACTS.merge(Code_Numbers_All_master_test[['ComponentID', 'CodeNumber', 'Description', 'MaterialGroup', 'MaterialSubCategory', 'BomInfo']],on='ComponentID', how='left')
            FACTS = FACTS.merge(Sourcer, on='SourcerID', how='left')
            FACTS = FACTS.merge(StorageLocation, on='StorageLocationID', how='left')
            FACTS = FACTS.merge(Location, on='LocationID', how='left')
            FACTS = FACTS.merge(code_correction[['CodeNumber', 'CodeNumber_Corrected']], on='CodeNumber', how='left')
            FACTS['CodeNumber_Corrected'] = FACTS['CodeNumber_Corrected'].fillna(FACTS['CodeNumber'])
            FACTS.drop(columns='CodeNumber', inplace=True)
            FACTS.rename(columns={'CodeNumber_Corrected':'CodeNumber'}, inplace=True)
            return FACTS

import pandas as pd

class DataProcessor:
    def __init__(self, mara, mw, wst, access_data):
        self.mara = mara
        self.mw = mw
        self.wst = wst
        self.access_data = access_data

    def convert_material_to_int(self):
        self.mara['Material'] = self.mara['A~Material'].astype(np.int64)
        print("mara\n",self.mara[self.mara['B~ErzNr_D']=='A3C40235900'])
        for df in [ self.mw, self.wst]:
            df['Material'] = df['Material'].astype(int)

    def merge_dataframes(self):
        mw_master_data = pd.merge(self.mara, self.mw, on='Material', how='outer')
        wst_master_data = pd.merge(self.mara, self.wst, on='Material', how='outer')
        
        
        self.master_data_all_sap = pd.concat([mw_master_data, wst_master_data])
        
    def aggregate_master_data(self):
        self.master_data_all_sap = self.master_data_all_sap.groupby(['Material'], dropna=False)\
                                                          .agg({'B~ErzNr_D':'first','B~Reserve1':'first','Customer PN':'first','Fujitsu P/N':'first', 
                                                                'B~MatArt':'first', 'C~EkGruppe':'first', 'B~jPDM-Nr':'first', 'B~jPDM-ST':'first'})\
                                                          .reset_index()

    def rename_columns(self):
        self.master_data_all_sap.rename(columns={'Material':'material_number', 'B~jPDM-Nr':'jpdm_number', 
                                                 'B~ErzNr_D':'sap_print_number', 'Customer PN':'mw_code', 
                                                 'Fujitsu P/N':'wst_code', 'B~MatArt':'material_type',
                                                 'B~jPDM-ST':'status', 'C~EkGruppe':'sourcer'}, inplace=True)



    def merge_access_with_master(self):
        merge_results = []
        for column in ['sap_print_number', 'mw_code', 'wst_code']:
            merged_df = pd.merge(self.access_data, self.master_data_all_sap, left_on='CodeNumber', right_on=column, how='left')
            merge_results.append(merged_df)
        self.final_df = pd.concat(merge_results)
        self.final_df = self.final_df.groupby(['CodeNumber'], dropna='False')[['material_number','sap_print_number', 'mw_code', 'wst_code', 'Description', 'status','MaterialGroup', 'MaterialSubCategory', 'LocationName', 'material_type',  'BOMID', 'BomInfo']].agg({ 'material_number':'first', 'sap_print_number':'first', 'mw_code':'first', 'wst_code':'first', 'Description':'first', 'status':'first','MaterialGroup':'first', 'MaterialSubCategory':'first','LocationName':'unique', 'material_type':'first', 'BOMID':'first', 'BomInfo':'first'}).reset_index()
        # print("after \n",self.final_df[self.final_df['CodeNumber']=='A3C40235900'])
    
    def process_data(self):
        self.convert_material_to_int()
        self.merge_dataframes()
        self.aggregate_master_data()
        self.rename_columns()
        codes_notin_jp10 = self.access_data[~((self.access_data['CodeNumber'].isin(self.master_data_all_sap['mw_code'].unique()))|
                                       (self.access_data['CodeNumber'].isin(self.master_data_all_sap['wst_code'].unique()))|
                                       (self.access_data['CodeNumber'].isin(self.master_data_all_sap['sap_print_number'].unique())))].groupby('CodeNumber')[['Description', 'LocationName', 'BOMID','BomInfo', 'DateID']].max().reset_index()
        
        # print("CODE NUMBERS THAT ARE IN INVENTORY FILES BUT NOT FOUND IN JP10 codes_notin_jp10 \n", codes_notin_jp10.head(5))

        
        self.merge_access_with_master()

        print("CODE NUMBERS THAT ARE IN INVENTORY FILES BUT NOT FOUND IN JP10 self.final_df \n", self.final_df[(self.final_df['material_number'].isnull())].head(5))
        # self.final_df.to_excel('material_number_to_code_number.xlsx', index=False)

        return self.final_df
    
class OO_Processor:
    def __init__(self, sap_oo, mw, wst, access_data):
        self.mara = mara
        self.mw = mw
        self.wst = wst
        self.access_data = access_data

def upload_data(data):
    with app.app_context():
        engine = db.engine
        data.to_sql('material', con=engine, index=False, if_exists='append')

if __name__ == "__main__":
    csv_handler = CSVHandler(r"C:\Users\KilicarslanS\OneDrive - FUJITSU\Dokumente\inventory_controlling_app_initial_data")
    excel_handler = XLSXHandler(r"C:\Users\KilicarslanS\OneDrive - FUJITSU\Dokumente\inventory_controlling_app_initial_data")
    access_handler = AccessDBHandler('//g02defssome02.g02.fujitsu.local/groups/PS&S_SCM/PBI/GLOBAL_INVENTORY_REPORTING/TOTAL INVENTORY REPORTING/Global Inventory Data Warehouse/TEST/Global_Inventory_test.accdb')

    mara = csv_handler.read_data('JP10_MARA.csv')
    mw_codes = csv_handler.read_data('MW_Codes.csv')
    wst_codes = csv_handler.read_data('WST_Codes.csv')
    code_number_corrector = excel_handler.read_data('Code_Number_Correction.xlsx')
    access_data = access_handler.read_data(code_number_corrector)

    # Usage:
    processor = DataProcessor(mara, mw_codes, wst_codes, access_data)
    final_df = processor.process_data()
    # upload_data(processed_data)
    print('Data processing and upload complete.')
