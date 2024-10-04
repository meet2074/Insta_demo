from sqlalchemy.orm import Session 
from sqlalchemy import desc
from fastapi import HTTPException,status
from src.resources.user.model import User
from src.resources.follow.model import Follower
from src.functions.like_functions.likes_function import get_name_by_user_id
from datetime import datetime,timezone
import uuid
def follow_a_user(db:Session,current_user_id:str,follower_id:str):
    try:
        if  current_user_id==follower_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Can't follow self!")
        current_user = db.query(User).filter(User.id==current_user_id).one()
        current_user.following+=1
        
        follower = db.query(User).filter(User.id==follower_id).one()
        follower.followers+=1
        
        followers = Follower(id=str(uuid.uuid4()),user_id=current_user_id,follower_id=follower_id,created_at=datetime.now(tz=timezone.utc))
        db.add(followers)
        db.commit()
        db.refresh(followers)
        
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(err))
    
def unfollow_a_user(db:Session,current_user_id:str,follower_id:str):
    try:

        current_user = db.query(User).filter(User.id==current_user_id).one()
        current_user.following-=1
        
        follower = db.query(User).filter(User.id==follower_id).one()
        follower.followers-=1
        
        db.query(Follower).filter(Follower.user_id==current_user_id,Follower.follower_id==follower_id).delete()
        db.commit()
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(err))

def is_followed(db:Session,current_user_id:str,follower_id:str):
    try:
        data = db.query(Follower).filter(Follower.user_id==current_user_id,Follower.follower_id==follower_id).one_or_none()
        if data:
            return True
        return False
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"A database error occred! {err}")
    
def get_followers(db:Session,id_of_user:str,page:int,limit:int):
    page = page*limit-limit
    try:
        data = db.query(Follower).filter(Follower.follower_id==id_of_user).order_by(desc(Follower.created_at)).offset(page).limit(limit)
        data
        names =  []
        for i in data:
            id = i.user_id
            time = i.created_at
            user = db.query(User).filter(User.id==id).one()
            firstname = user.first_name
            lastname = user.last_name
            names.append({"full-name":firstname +" "+ lastname,"user_id":id,"Followed_at":time})
        return names
    except Exception as err:
        raise HTTPException(status_code=500,detail=str(err))

def get_following(db:Session,id_of_user:str,page:int,limit:int):
    page = page*limit-limit
    try:
        data = db.query(Follower).filter(Follower.user_id==id_of_user).order_by(desc(Follower.created_at)).offset(page).limit(limit)
        names =  []
        for i in data:
            id = i.follower_id
            user = db.query(User).filter(User.id==id).one()
            firstname = user.first_name
            lastname = user.last_name
            names.append({"full-name":firstname +" "+ lastname,"user_id":id})
        return names
    except Exception as err:
        raise HTTPException(status_code=500,detail=str(err))

def get_count_followers_and_following(db:Session,id:str):
    data = db.query(User).filter(User.id == id).one()
    return {"Followers":data.followers,"Following":data.following}