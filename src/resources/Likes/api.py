from fastapi import FastAPI,APIRouter,Depends
from src.functions.likes_function import *
from Database.database import get_db
from sqlalchemy.orm import Session
from src.functions.user_function import verify_token

router = APIRouter()


@router.get("/posts/{post_id}/like")
def like_post(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    userid = payload.get("id")
    has_liked = has_user_liked(db,userid,post_id)
    # breakpoint()
    if not has_liked:
        post_like(db,post_id)
        return "liked!"
    else:
        post_dislike(db,post_id)
        return "disliked!"

@router.get("/posts/{post_id}/liked_by")
def liked_by(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    data = posts_liked_by(db,post_id)
    return data
