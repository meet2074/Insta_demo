from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.resources.Posts.model import Posts
from src.resources.Likes.model import likes
from src.resources.user.model import User


def post_like(db: Session, postid: str):
    try:
        data = db.query(Posts).filter(Posts.id == postid).one()
        data.likes += 1
        db.commit()

        userid = get_user_id_from_post_id(db, postid)
        like_data = likes(post_id=postid, user_id=userid)
        db.add(like_data)
        db.commit()
        db.refresh(like_data)
        return True
    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


def post_dislike(db: Session, postid: str):
    try:
        data = db.query(Posts).filter(Posts.id == postid).one()
        data.likes -= 1
        db.commit()

        data2 = db.query(likes).filter(likes.post_id == postid).delete()
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


def posts_liked_by(db: Session, postid: str):
    data = db.query(likes).filter(likes.post_id == postid).all()
    
    u_id = []
    names = []
    for i in data:
        u_id.append(i["user_id"])
    for i in u_id:
        name = get_name_by_user_id(db, i)
        names.append(name)
    return names


def has_user_liked(db: Session, user_id: str, post_id: str):

    data = db.query(likes).filter(likes.user_id == user_id).one_or_none()
    if not data:
        return False
        # raise HTTPException(status_code=404,detail=str(err))
    # breakpoint()
    if data.post_id == post_id:
        return True
    return False
