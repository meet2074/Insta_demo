from fastapi import APIRouter,Depends,status,Query
from sqlalchemy.orm import Session
from src.functions.post_functions.post_function import *
from src.functions.user_functions.user_function import verify_token
from src.resources.posts import schemas
from database.database import get_db
from src.functions.like_functions.likes_function import get_user_id_from_post_id


router = APIRouter()

@router.get("/allpost",response_model=dict[str,schemas.get_post])
def get_all_post(db:Session = Depends(get_db),payload:dict = Depends(verify_token),limit:int = Query(10,ge=1),offset:int = Query(0,ge=0)):
    post = get_post_all(db,limit,offset)
    return post

@router.get("/posts", response_model=list[schemas.get_post])
def get_posts(db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    id = payload.get("id")
    data = get_post_by_id(db,id)
    return data


@router.get("/posts/{post_id}",response_model=schemas.get_post)
def get_single_post(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    id = payload.get("id")
    if id!=get_user_id_from_post_id(db,post_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated!")
    post = get_one_post(db,post_id)
    return post

@router.post("/posts/create_post")
def create_new_post(post:schemas.post_create,db:Session = Depends(get_db),payload :dict = Depends(verify_token)):
    id = payload.get("id")
    create_post(db,id,post)
    return "Post created successfully!"

@router.put("/posts/update_post/{post_id}")
def update_a_post(post_schema:schemas.post_update,post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    id = payload.get("id")
    if id!=get_user_id_from_post_id(db,post_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated!")
    update_post(db,post_id,post_schema)
    return "Post updated successfully!"

@router.delete("/posts/delete/{post_id}")
def delete(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
    id = payload.get("id")
    if id!=get_user_id_from_post_id(db,post_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated!")
    delete_post(db,post_id)
    return "Post deleted successfully!"