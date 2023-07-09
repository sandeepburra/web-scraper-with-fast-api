from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
# Create the FastAPI instance
app = FastAPI()
pg_connection_dict = {
    'dbname': "fastapi_database",
    'user': "postgres",
    'password': "password",
    'port': "5432",
    'host': "postgres"
}
conn = psycopg2.connect(**pg_connection_dict)
engine = create_engine(f"postgresql+psycopg2://postgres:{pg_connection_dict['password']}" +
            f"@{pg_connection_dict['user']}:{pg_connection_dict['port']}/{pg_connection_dict['dbname']}")

class ForParts(BaseModel):
    manufacturer: str = Field(examples=["Ammann"])
    model: str = Field(examples=["ASC100"])
    
class ForModels(BaseModel):
    manufacturer: str  = Field(examples=["Ammann"])

@app.post("/getmodels/")
async def query_endpoint(params: ForModels):
    # Extract the query parameters
    manufacturer = params.manufacturer
    
    # Create a connection to the SQLite database
    
    
    query = f"SELECT distinct models.model from Manufacturer\
        JOIN category on manufacturer.manufacturer_id = category.manufacturer_id\
        join models on category.category_id = models.category_id\
        where Manufacturer.manufacturer = '{manufacturer}'"
    df = pd.read_sql(query, engine)
    
    result = {'Manufacturer': manufacturer, 'models': df["model"].tolist()}
   

    # Return the query result
    if not result:
        raise HTTPException(status_code=404, detail="No matching records found")
    
        
    return result


@app.post("/getparts/")
async def query_endpoint(params: ForParts):
    # Extract the query parameters
    manufacturer = params.manufacturer
    model = params.model
    
    # Create a connection to the SQLite database
    
    
    query = f"SELECT Parts.part_number,Parts.part_name from Manufacturer\
        JOIN category on manufacturer.manufacturer_id = category.manufacturer_id\
        join models on category.category_id = models.category_id\
        JOIN Parts on models.model_id = Parts.model_id\
        where Manufacturer.manufacturer = '{manufacturer}' and\
        models.model = '{model}'"
    df = pd.read_sql(query, engine)

    parts_data = df.to_dict(orient='records')
    
    result = {'Manufacturer': manufacturer, 'model': model, 'parts': parts_data}
   

    # Return the query result
    if not result:
        raise HTTPException(status_code=404, detail="No matching records found")
    
        
    return result


@app.get("/")
async def root():
    return {"message": "Hello World"}




