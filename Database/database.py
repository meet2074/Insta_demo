from sqlalchemy import create_engine
from config import DATABASE_URL

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv  
# from src.resources.user import model

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
load_dotenv() 


# database_url = os.getenv("DATABASE_URL")

engine = create_engine(url=DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()





