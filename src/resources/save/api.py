from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.functions.user_functions.user_function import verify_token
from database.database import get_db
from src.functions.save_functions.save_function import *
from src.resources.save.schema import SaveResponse
from src.functions.post_functions.post_function import get_one_post

router = APIRouter()


@router.post("/post/{postid}/save")
def save_post(
    postid: str, db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):
    id = payload.get("id")
    saved = is_saved(db, postid, id)
    if not saved:
        save_a_post(db, postid, id)
        return "saved!"
    else:
        unsave_a_post(db, postid, id)
        return "Unsaved!"


@router.get("/saved")
def get_saved(
    db: Session = Depends(get_db),
    page_no: int = Query(default=1),
    limit: int = Query(default=5),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    posts = get_all_saved_post(db, page_no, limit, id)
    return posts


