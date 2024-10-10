from fastapi import FastAPI
from src.resources.likes.api import router as likerouter
from src.resources.user.api import router as userrouter
from src.resources.posts.api import router as postrouter
from src.resources.follow.api import router as followrouter
from src.resources.comment.api import router as commentrouter
from src.resources.save.api import router as saverouter
from src.resources.user import model
import uvicorn


app = FastAPI()

app.include_router(userrouter)
app.include_router(postrouter)
app.include_router(likerouter)
app.include_router(followrouter)
app.include_router(commentrouter)
app.include_router(saverouter)


