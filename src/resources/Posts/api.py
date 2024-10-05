from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Body, Response
from fastapi.responses import JSONResponse
from typing import Union

# from fastapi import Response
import base64
from sqlalchemy.orm import Session
from src.functions.post_functions.post_function import *
from src.resources.posts.model import *
from src.functions.user_functions.user_function import verify_token
from src.resources.posts import schemas
from database.database import get_db
from src.functions.like_functions.likes_function import get_user_id_from_post_id


router = APIRouter()


@router.get("/allpost", response_model=list[schemas.get_post])
def get_all_post(
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
    limit: int = Query(default=5),
    page: int = Query(default=1),
):
    post = get_post_all(db, limit, page)
    return post


@router.get("/posts", response_model=list[schemas.get_post])
def get_posts(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    id = payload.get("id")
    data = get_post_by_id(db, id)
    return data


# @router.get("/posts/{post_id}/image")
# def get_single_post(post_id:str,db:Session = Depends(get_db),payload:dict = Depends(verify_token)):
#     id = payload.get("id")
#     if id!=get_user_id_from_post_id(db,post_id):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated!")
#     post = get_one_post(db,post_id)
#     if post is None:
#         raise HTTPException(status_code=404, detail="Post not found")
#     # breakpoint()
#     return {"image":Response(content=post.data, media_type="image/avif"),"captions":post.captions,"likes":post.likes}


@router.get("/posts/{post_id}/image")
def get_image(post_id: str, db: Session = Depends(get_db)):
    post_record = db.query(Posts).filter(Posts.id == post_id).first()

    if post_record is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post = get_one_post(db, post_id)

    return Response(content=post.data, media_type="image/avif") 


@router.get("/posts/{post_id}")
def get_post(
    post_id: str, db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):
    user_id = payload.get("id")

    if user_id != get_user_id_from_post_id(db, post_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated!"
        )

    post = get_one_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    image_data_base64 = base64.b64encode(post.data).decode("utf-8")

    return JSONResponse(
        content={
            "image": Response(content=post.data, media_type="image/jpeg"),
            "image": image_data_base64,
            "captions": post.captions,
            "likes": post.likes,
        }
    )


@router.post("/posts/create_post")
def create_new_post(
    data: UploadFile = File(...),
    captions: str = Body(),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    image_file = data.file.read()
    create_post(db, id, image_file, captions)
    return "Post created successfully!"


@router.put("/posts/update_post/{post_id}")
def update_a_post(
    post_schema: schemas.post_update,
    post_id: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    if id != get_user_id_from_post_id(db, post_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated!"
        )
    update_post(db, post_id, post_schema)
    return "Post updated successfully!"


@router.delete("/posts/delete/{post_id}")
def delete(
    post_id: str, db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):
    id = payload.get("id")
    if id != get_user_id_from_post_id(db, post_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated!"
        )
    delete_post(db, post_id)
    return "Post deleted successfully!"


@router.post("/image")
def upload_image(data: UploadFile = File(...), db: Session = Depends(get_db)):
    image_content = data.file.read()
    image_upload(db, image_content)
    data.file.close()
    return "uploaded"
