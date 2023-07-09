import psycopg2
from pandas import DataFrame
from sqlalchemy import create_engine
import pandas as pd

class MasterDB():
    def __init__(self):
        self.env_variables = self.__get_environment_variables()
        self.conn = self.__initialize_db()
        self.engine = self.__create_engine()
        
    def __get_environment_variables(self):
        pg_connection_dict = {
            'dbname': "fastapi_database",
            'user': "postgres",
            'password': "password",
            'port': "5432",
            'host': "postgres"
        }
        return pg_connection_dict
    def __initialize_db(self):
        """creating the DB and the required tables"""
        
        conn = psycopg2.connect(**self.env_variables)
        cursor = conn.cursor()
        
        # Create manufacturer able
        cursor.execute('''CREATE TABLE IF NOT EXISTS manufacturer
                        (manufacturer_id INTEGER PRIMARY KEY,
                        manufacturer TEXT)''')

        # Create category table
        cursor.execute('''CREATE TABLE IF NOT EXISTS category
                        (category_id INTEGER PRIMARY KEY,
                        manufacturer_id INTEGER,
                        category TEXT,
                        FOREIGN KEY (manufacturer_id) REFERENCES manufacturer (manufacturer_id))''')

        # Create models table
        cursor.execute('''CREATE TABLE IF NOT EXISTS models
                        (model_id INTEGER PRIMARY KEY,
                        category_id INTEGER,
                        model TEXT,
                        FOREIGN KEY (category_id) REFERENCES category (category_id))''')

        # Create parts table
        cursor.execute('''CREATE TABLE IF NOT EXISTS parts
                        (part_id INTEGER PRIMARY KEY,
                        part TEXT,
                        part_number TEXT,
                        part_name TEXT,
                        model_id INTEGER,
                        FOREIGN KEY (model_id) REFERENCES models (model_id))''')

        conn.commit()
        return conn
    
    def __create_engine(self):
        
        engine = create_engine(f"postgresql+psycopg2://postgres:{self.env_variables['password']}" +
            f"@{self.env_variables['user']}:{self.env_variables['port']}/{self.env_variables['dbname']}")
        print(engine)
        return engine
        
    def save_df_to_db(self, df: DataFrame, table_name:str):
        """saving dataframe to db.

        Args:
            df (DataFrame): Dataframe to be saved in the DB table
            table_name (str): Table name to be saved
        """
            
        df.to_sql(table_name, self.engine, if_exists='append', index=False)
        
    
    def close(self):
        """Closing DB connection"""
        self.conn.commit()
        self.conn.close()
    
    