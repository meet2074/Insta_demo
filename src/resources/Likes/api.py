from fastapi import FastAPI,APIRouter,Depends
from src.functions.like_functions.likes_function import *
from database.database import get_db
from sqlalchemy.orm import Session
from src.functions.user_functions.user_function import verify_token

router = APIRouter()


@router.get("/posts/{post_id}/like")
def like_post(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    userid = payload.get("id")
    has_liked = has_user_liked(db,userid,post_id)
    # breakpoint()
    if not has_liked:
        post_like(db,post_id,userid)
        return True
    else:
        post_dislike(db,post_id,userid)
        return False

@router.get("/posts/{post_id}/liked_by")
def liked_by(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    data = posts_liked_by(db,post_id)
    return data
