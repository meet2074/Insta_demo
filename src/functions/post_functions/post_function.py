from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.resources.likes.model import *
from src.resources.posts.model import *
from src.resources.posts.schemas import *
from datetime import datetime


def create_post(db: Session, user_id: str, post: post_create):
    if post.data is None:
        raise HTTPException(status_code=400, detail="Please upload the photo!")

    try:
        post_data = Posts(user_id=user_id, data=post.data, captions=post.captions)
        db.add(post_data)
        db.commit()
        db.refresh(post_data)
    except Exception as err:
        raise HTTPException(status_code=403, detail=str(err))


def update_post(db: Session, post_id: str, post=post_update):
    if post_id is None:
        raise HTTPException(status_code=404, detail="no post!")

    try:
        data = db.query(Posts).filter(Posts.id == post_id).one()
        # data.data = post.data
        if post.captions is not None:
            data.captions = post.captions
        if post.data is not None:
            data.data = post.data

        data.updated_at = datetime.now()
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
    data = db.query(Posts).filter(Posts.id == post_id).one()
    return data


def get_post_by_id(db: Session, user_id: str):
    try:
        data = db.query(Posts).filter(Posts.user_id == user_id).all()

        return data
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


def get_post_all(db: Session, limit: int, offset: int):
    posts_list = db.query(Posts).offset(offset).limit(limit).all()
    
    return posts_list
