import app
from app import uvicorn
from database.connection import *

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)