from sqlalchemy.orm import Session
from fastapi import HTTPException,Body
from src.resources.comment.model import Comments
from src.resources.user.model import User
from src.resources.posts.model import Posts
import uuid
from datetime import datetime, timezone


def make_comment(db: Session, post_id: str, userid: str, data: str = Body()):
    try:
        post = db.query(Posts).filter(Posts.id == post_id).one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="No post found!")
        data = Comments(
            id=str(uuid.uuid4()),
            userid=userid,
            postid=post_id,
            data=data,
            created_at=datetime.now(tz=timezone.utc),
        )

        db.add(data)
        post.comments += 1
        db.commit()
        db.refresh(data)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_all_comments_of_post(db: Session, postid: str, pageno: int, limit: int):
    pageno = pageno * limit - limit
    try:
        post = db.query(Posts).filter(Posts.id == postid).one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="No post found!")
        data = (
            db.query(Comments)
            .filter(Comments.postid == postid)
            .offset(pageno)
            .limit(limit)
            .all()
        )
        if len(data)==0  :
            raise HTTPException(status_code=404,detail="No comments yet!")
        res = []
        for i in data:
            if not i.is_deleted:
                res.append(i)
        return res 
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_single_comment_by_id(db: Session, postid: str, comment_id: str):
    try:
        data = (
            db.query(Comments)
            .filter(Comments.postid == postid, Comments.id == comment_id)
            .one_or_none()
        )
        if data is None or data.is_deleted:
            raise HTTPException(status_code=404,detail="NO comments Found!")
        
        return data
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def get_all_comments_of_a_user(db: Session, userid: str, pageno: int, limit: int):
    pageno = pageno * limit - limit
    try:
        data = (
            db.query(Comments)
            .filter(Comments.userid == userid)
            .offset(pageno)
            .limit(limit)
            .all()
        )
        if len(data)==0:
            raise HTTPException(status_code=404,detail="NO comments yet!")
        res = []
        for i in data:
            if not i.is_deleted:
                res.append(i)
        return res 
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


def delete_comment(db: Session, post_id: str, comment_id: str, current_userid: str):
    try:
        commenter_id = db.query(Comments).filter(Comments.id == comment_id).one().userid
        if commenter_id == current_userid:
            data = db.query(Comments).filter(Comments.id == comment_id).one()
            if data.is_deleted:
                raise HTTPException(status_code=404,detail="No comments exist!")
            data.is_deleted = True
            post = db.query(Posts).filter(Posts.id == post_id).one_or_none()
            post.comments -= 1
            db.commit()
            return True

        post_owner_id = db.query(Posts).filter(Posts.id == post_id).one().user_id
        if post_owner_id == current_userid:
            data = db.query(Comments).filter(Comments.id == comment_id).one()
            if data.is_deleted:
                raise HTTPException(status_code=404,detail="No comments exist!")
            data.is_deleted = True
            post = db.query(Posts).filter(Posts.id == post_id).one_or_none()
            post.comments -= 1
            db.commit()
            return True
        else:
            raise HTTPException(status_code=401,detail="Can not delete others comment!")
        


    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
