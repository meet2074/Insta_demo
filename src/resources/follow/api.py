from database import database
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends
from typing import Optional
from src.functions.user_functions.user_function import verify_token
from src.functions.follow_functions.follow_functions import *


router = APIRouter()

@router.post("/profile/{follower_id}/follow")
def follow_the_profile(follower_id:str,payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    user_id = payload.get("id")
    followed = is_followed(db,user_id,follower_id)
    if not followed:
        follow_a_user(db,current_user_id=user_id,follower_id=follower_id)
        # breakpoint()
        return "Followed!"
    else:
        unfollow_a_user(db,user_id,follower_id=follower_id)
        return "Unfollowed!"

@router.get("/profile/{follower_id}/followers")
def get_all_followers(follower_id:str,payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    followers = get_followers(db,follower_id)
    return followers

@router.get("/profile/followers")
def get_all_followers(payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    id = payload.get("id")
    followers = get_followers(db,id)
    return followers

@router.get("/profile/{follower_id}/following")
def get_all_following(follower_id:Optional[str|None]=None,payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    followers = get_following(db,follower_id)
    return followers

@router.get("/profile/following")
def get_all_following(payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    id = payload.get("id")
    followers = get_following(db,id)
    return followers
    