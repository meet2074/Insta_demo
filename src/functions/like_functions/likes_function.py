from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from src.resources.posts.model import Posts
from src.resources.likes.model import likes
from src.resources.user.model import User
import uuid


def post_like(db: Session, postid: str, userid: str):
    try:
        data = db.query(Posts).filter(Posts.id == postid).one()
        data.likes += 1
        db.commit()

        like_data = likes(id=str(uuid.uuid4()), post_id=postid, user_id=userid)
        db.add(like_data)
        db.commit()
        db.refresh(like_data)
        return True
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


def post_dislike(db: Session, postid: str, userid: str):
    try:
        data = db.query(Posts).filter(Posts.id == postid).one()
        data.likes -= 1
        db.commit()

        db.query(likes).filter(
            likes.user_id == userid, likes.post_id == postid
        ).delete()
        # db.delete(data2)
        db.commit()
        return True
    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


def get_user_id_from_post_id(db: Session, postid: str):
    data = db.query(Posts).filter(Posts.id == postid).one()
    user_id = data.user_id
    return user_id


def get_name_by_user_id(db: Session, user_id: str):
    data = db.query(User).filter(User.id == user_id).one()
    return data.first_name


def posts_liked_by(db: Session, postid: str,page:int,limit:int):
    page = page*limit - limit
    data = db.query(likes).filter(likes.post_id == postid).offset(page).limit(limit).all()

    names = []
    for i in data:
        id = i.user_id
        name = get_name_by_user_id(db, id)
        names.append(name)
    return names


def has_user_liked(db: Session, user_id: str, post_id: str):
    try:
        data = (
            db.query(likes)
            .filter(likes.user_id == user_id, likes.post_id == post_id)
            .one_or_none()
        )
        if not data:
            return False
            # raise HTTPException(status_code=404,detail=str(err))
        # breakpoint()
        if data.post_id == post_id:
            return True
        return False
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not found")
