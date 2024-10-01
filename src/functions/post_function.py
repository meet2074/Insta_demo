from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.resources.Likes.model import *
from src.resources.Posts.model import *
from src.resources.Posts.schemas import *

def create_post(db:Session,user_id:str,post:post_create):
    if post.data is None:
        raise HTTPException(status_code=400,detail="Please upload the photo!")
    
    try:
        post_data = Posts(user_id=user_id,data=post.data,captions=post.captions)
        db.add(post_data)
        db.commit()
        db.refresh(post_data)
    except Exception as err:
        raise HTTPException(status_code=403,detail=str(err))
    
def update_post(db:Session,post_id:str,post= post_update):
    if post_id is None:
        raise HTTPException(status_code=404, detail="no post!")
    
    try:
        data = db.query(Posts).filter(Posts.id==post_id).one()
        data.data = post.data
        if data.captions is None:
            data.captions = post.captions
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=401,detail=str(err))
    
def get_post_from_userid(db:Session,user_id:str):
    data = db.query(Posts)
    
def delete_post(db:Session,post_id:str):
    try:
        data = db.query(Posts).filter(Posts.id==post_id).one()
        data.is_deleted = True
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=404,detail=str(err))
    
def get_one_post(db:Session,post_id:str):
    data = db.query(Posts).filter(Posts.id==post_id).one()
    return data
def get_post_by_id(db:Session,user_id:str):
    li = []
    try:
        data = db.query(Posts).filter(Posts.user_id==user_id).all()
        
    except Exception as err:
        raise HTTPException(status_code=400,detail=str(err))
    return data
    
def get_liked_by(db:Session,post_id:str):
    data=db.query(likes).filter(likes.post_id==post_id).filter()
    # list = []
    # for i in data:
    #     list.append(i[])
    return True

    
    