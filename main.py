from fastapi import FastAPI
from src.resources.Likes.api import router as likerouter
from src.resources.user.api import router as userrouter
from src.resources.Posts.api import router as postrouter
import uvicorn
from src.resources.user import model
from Database.database import engine
try:
    model.Base.metadata.create_all(engine)
    print("Connection successful!!")
except Exception as err:
    print(err)


app = FastAPI()

app.include_router(userrouter)
app.include_router(postrouter)
app.include_router(likerouter)


if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)