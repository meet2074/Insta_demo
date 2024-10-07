from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from database.database import get_db
from src.functions.user_functions.user_function import verify_token
from src.functions.comment_functions.coment_functions import *
from src.resources.comment.schemas import AllCommnetsRespons,CreateComment

router = APIRouter()


@router.post("/post/{post_id}/c")
def comment_on_post(
    post_id: str,
    data:CreateComment ,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    # breakpoint()
    userid = payload.get("id")
    make_comment(db, post_id, userid,data.comment)
    return "Successfully commented!"


@router.get("/post/{postid}/comments", response_model=list[AllCommnetsRespons])
def get_comments(
    postid: str,
    db: Session = Depends(get_db),
    page_no: int = Query(default=1),
    limit: int = Query(default=5),
    payload: dict = Depends(verify_token),
):
    comments = get_all_comments_of_post(db, postid, page_no, limit)
    return comments


@router.get("/post/{postid}/comments/{comment_id}", response_model=AllCommnetsRespons)
def get_one_comment(
    postid: str,
    comment_id: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    comment = get_single_comment_by_id(db, postid, comment_id)
    return comment


@router.get("/profile/comments", response_model=list[AllCommnetsRespons])
def all_comments_of_user(
    db: Session = Depends(get_db),
    page_no: int = Query(default=1),
    limit: int = Query(default=5),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    data = get_all_comments_of_a_user(db, id, page_no, limit)
    return data


@router.delete("/post/{postid}/comments/{commentid}/delete")
def delete_a_comment(
    postid: str,
    commentid: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    
    delete_comment(db, postid, commentid,id)
    return "Deleted successfully!"
