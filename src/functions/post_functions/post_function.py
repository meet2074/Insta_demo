from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.resources.likes.model import *
from src.resources.posts.model import *
from src.resources.posts.schemas import *
from datetime import datetime


def create_post(
    db: Session, user_id: str, data: bytes | str, captions: str, data_type: str
):
    if data is None:
        raise HTTPException(status_code=400, detail="Please upload the photo!")

    try:
        if type(data) == bytes:
            post_data = Posts(
                id=str(uuid.uuid4()),
                user_id=user_id,
                file_data=data,
                type=data_type,
                captions=captions,
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            db.add(post_data)
            db.commit()
            db.refresh(post_data)
        else:
            post_data = Posts(
                id=str(uuid.uuid4()),
                user_id=user_id,
                text_data=data,
                type=data_type,
                captions=captions,
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
            )
            db.add(post_data)
            db.commit()
            db.refresh(post_data)
    except Exception as err:
        raise HTTPException(status_code=403, detail=str(err))


def update_post(
    db: Session, post_id: str, data: bytes | str, captions: str, content_type: str
):
    if post_id is None:
        raise HTTPException(status_code=404, detail="no post!")

    try:
        data_type = type(data)
        query_data = db.query(Posts).filter(Posts.id == post_id).one()
        if data_type is str:
            if captions is not None:
                query_data.captions = captions
            if data is not None:
                query_data.text_data = data
                query_data.file_data = None
                query_data.type = content_type
        else:
            if captions is not None:
                query_data.captions = captions
            if data is not None:
                query_data.file_data = data
                query_data.text_data = None
                query_data.type = content_type

        query_data.updated_at = datetime.now()
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=401, detail=str(err))


def delete_post(db: Session, post_id: str):
    try:
        data = db.query(Posts).filter(Posts.id == post_id).one()
        data.is_deleted = True
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_one_post(db: Session, post_id: str):
    try:
        data = db.query(Posts).filter(Posts.id == post_id).one_or_none()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    return data


def get_post_by_id(db: Session, user_id: str):
    try:
        data = db.query(Posts).filter(Posts.user_id == user_id).all()
        for i in data:
            url = f"/posts/{i.id}/data"
            i.data = url
        return data
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


def get_post_all(db: Session, limit: int, page: int):
    page = page * limit - limit
    try:
        posts_list = db.query(Posts).offset(page).limit(limit).all()

        for i in posts_list:
            url = f"/posts/{i.id}/data"
            i.data = url
        return posts_list
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


# def data_upload(db: Session, data: bytes):
#     data = Image(id=str(uuid.uuid4()), image=data)
#     db.add(data)
#     db.commit()
#     db.refresh(data)
