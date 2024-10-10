from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Body, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union
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


@router.get("/posts/{post_id}/data")
def get_image(post_id: str, db: Session = Depends(get_db)):
    post_record = db.query(Posts).filter(Posts.id == post_id).first()

    if post_record is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post = get_one_post(db, post_id)
    if post.type == "image":
        return Response(content=post.file_data, media_type="image/jpeg")
    elif post.type == "video":
        return Response(content=post.file_data, media_type="video/mp4")
    else:
        return Response(content=post.text_data, media_type="text/plain")


@router.get("/post/{post_id}")
def get_post(
    post_id: str, db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):

    post = get_one_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.type == "text":
        return JSONResponse(
            content={
                "post_id": post_id,
                "data": post.text_data,
                "captions": post.captions,
                "likes": post.likes,
            }
        )
    else:
        data_url = f"/posts/{post_id}/data"
        return JSONResponse(
            content={
                "post_id": post_id,
                "data": data_url,
                "captions": post.captions,
                "likes": post.likes,
            }
        )


@router.post("/posts/create_post")
def create_new_post(
    data: Union[UploadFile, str] = File(None),
    captions: str = Body(),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    data_type = type(data)
    content_type = None
    id = payload.get("id")

    if data_type is str:
        content_type = "text"
        create_post(db, id, data, captions, content_type)
    else:
        data_type = data.content_type
        if data_type.startswith("image/"):
            content_type = "image"
        elif data_type.startswith("video/"):
            content_type = "video"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type!")

        data_file = data.file.read()
        create_post(db, id, data_file, captions, content_type)
    return "Post created successfully!"


@router.put("/posts/update_post/{post_id}")
def update_a_post(
    post_id: str,
    captions: str = Body(None),
    data: UploadFile | str = File(None),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    id = payload.get("id")
    if id != get_user_id_from_post_id(db, post_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated!"
        )
    data_file = None
    content_type = None
    if type(data) is str:
        data_file = data
        content_type = "text"
        update_post(db, post_id, data_file, captions, content_type)
    else:
        data_type = data.content_type
        if data_type.startswith("image/"):
            content_type = "image"
        elif data_type.startswith("video/"):
            content_type = "video"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type!")

        data_file = data.file.read()
        update_post(db, post_id, data_file, captions, content_type)
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
