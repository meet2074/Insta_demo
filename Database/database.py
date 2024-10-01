from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
load_dotenv() 

database_url = os.getenv("DATABASE_URL")

engine = create_engine(url=database_url)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()



