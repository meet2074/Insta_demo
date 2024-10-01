from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from src.functions.post_function import *
from src.functions.user_function import verify_token
from src.resources.Posts import schemas
from Database.database import get_db

router = APIRouter()

@router.get("/posts", response_model=list[schemas.get_post])
def get_all_post(db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    id = payload.get("id")
    data = get_post_by_id(db,id)
    return data

@router.get("/posts/{post_id}",response_model=schemas.get_post)
def get_single_post(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    post = get_one_post(db,post_id)
    return post

@router.post("/posts/create_post")
def create_new_post(post:schemas.post_create,db:Session = Depends(get_db),payload :dict = Depends(verify_token)):
    id = payload.get("id")
    create_post(db,id,post)
    return "Post created successfully!"

@router.put("/posts/update_post/{post_id}")
def update_a_post(post_schema:schemas.post_update,post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    update_post(db,post_id,post_schema)
    return "Post updated successfully!"

@router.delete("/posts/delete/{post_id}")
def delete(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    delete_post(db,post_id)
    return "Post deleted successfully!"