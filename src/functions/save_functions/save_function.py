from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from src.resources.save.model import Save
from src.resources.posts.model import Posts
from datetime import datetime, timezone
import uuid


def save_a_post(db: Session, postid: str, userid: str):
    try:
        is_post = db.query(Posts).filter(Posts.id == postid).one_or_none()
        if not is_post:
            raise HTTPException(status_code=404, detail="No such post exist!")
        data = Save(
            id=str(uuid.uuid4()),
            postid=postid,
            userid=userid,
            created_at=datetime.now(tz=timezone.utc),
        )

        db.add(data)
        db.commit()
        db.refresh(data)

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )


def unsave_a_post(db: Session, postid: str, userid: str):
    try:
        db.query(Save).filter(Save.postid == postid, Save.userid == userid).delete()
        db.commit()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )


def is_saved(db: Session, postid: str, userid: str):
    try:
        is_post = db.query(Posts).filter(Posts.id == postid).one_or_none()
        if not is_post:
            raise HTTPException(status_code=404, detail="No such post exist!")

        data = (
            db.query(Save)
            .filter(Save.userid == userid, Save.postid == postid)
            .one_or_none()
        )
        if not data:
            return False
        return True
    except Exception as err:
        raise HTTPException


def get_all_saved_post(db: Session, page_no: int, limit: int, userid: str):
    try:
        page_no = page_no * limit - limit
        data = (
            db.query(Save)
            .filter(Save.userid == userid)
            .offset(page_no)
            .limit(limit)
            .all()
        )

        res = {}
        count = 1
        for i in data:
            url = f"/post/{i.postid}"
            res[f"post{count}"] = url
            count += 1
        return res
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
