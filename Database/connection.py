# from src.resources.user import model 
from database.database import engine,Base


try:
    Base.metadata.create_all(engine)
    
    print("Connection successful!!")
except Exception as err:
    print(err)
