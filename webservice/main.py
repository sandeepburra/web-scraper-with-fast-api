from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Create the FastAPI instance
app = FastAPI()

# for demo

# Define the SQLAlchemy database connection
pg_connection_dict = {
    'dbname': "fastapi_database",
    'user': "postgres",
    'password': "password",
    'port': "5432",
    'host': "postgres"
}

# Create the SQLAlchemy engine and session
engine = create_engine(f"postgresql+psycopg2://{pg_connection_dict['user']}:{pg_connection_dict['password']}" +
                       f"@{pg_connection_dict['host']}:{pg_connection_dict['port']}/{pg_connection_dict['dbname']}")
SessionLocal = sessionmaker(bind=engine)

# Create the SQLAlchemy Base model
Base = declarative_base()


# Define the ORM models
class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    manufacturer_id = Column(Integer, primary_key=True)
    manufacturer = Column(String)
    categories = relationship('Category', back_populates='manufacturer')


class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.manufacturer_id'))
    category = Column(String)
    manufacturer = relationship('Manufacturer', back_populates='categories')
    models = relationship('Model', back_populates='category')


class Model(Base):
    __tablename__ = 'models'
    model_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.category_id'))
    model = Column(String)
    category = relationship('Category', back_populates='models')
    parts = relationship('Parts', back_populates='model')


class Parts(Base):
    __tablename__ = 'parts'
    part_id = Column(Integer, primary_key=True)
    part = Column(String)
    model_id = Column(Integer, ForeignKey('models.model_id'))
    model = relationship('Model', back_populates='parts')
    part_number = Column(String)
    part_name = Column(String)


# Create the database tables
Base.metadata.create_all(bind=engine)


class ForParts(BaseModel):
    manufacturer: str = Field(examples=["Ammann"])
    model: str = Field(examples=["ASC100"])


class ForModels(BaseModel):
    manufacturer: str = Field(examples=["Ammann"])


@app.get("/getmodels/")
async def get_manufacturer_models(manufacturer: str = Query(..., description="Manufacturer name")):

    # Create a session
    session = SessionLocal()

    try:
        # Query the models for the manufacturer
        models = session.query(Model.model).join(Category).join(Manufacturer). \
            filter(Manufacturer.manufacturer == manufacturer).distinct().all()

        # Convert the query result to a list
        model_list = [model[0] for model in models]

        result = {'Manufacturer': manufacturer, 'models': model_list}

        # Return the query result
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the session
        session.close()


@app.post("/getparts/")
async def get_model_parts(params: ForParts):
    # Extract the query parameters
    manufacturer = params.manufacturer
    model = params.model

    # Create a session
    session = SessionLocal()

    try:
        # Query the parts for the manufacturer and model
        parts = session.query(Parts.part_number, Parts.part_name).join(Model).join(Category).join(Manufacturer). \
            filter(Manufacturer.manufacturer == manufacturer, Model.model == model).all()

        # Convert the query result to a list of dictionaries
        parts_data = [{'part_number': part.part_number, 'part_name': part.part_name} for part in parts]

        result = {'Manufacturer': manufacturer, 'model': model, 'parts': parts_data}

        # Return the query result
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the session
        session.close()


@app.get("/")
async def test():
    return {"message": "Hello World"}

@app.get("/healthcheck")
async def test():
    return "healthy"