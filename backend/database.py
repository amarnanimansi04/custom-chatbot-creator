from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load all variables from your .env file
load_dotenv()

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the connection to Supabase
engine = create_engine(DATABASE_URL)

# Each API request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all models will inherit from
Base = declarative_base()

# This function gives us a DB session and closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()