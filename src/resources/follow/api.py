from database import database
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,Query,Path
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
        return "Followed!"
    else:
        unfollow_a_user(db,user_id,follower_id=follower_id)
        return "Unfollowed!"
    
    
@router.get("/profile/followers")
def get_all_followers(id:Optional[str|None] = None,page_no:int = Query(default=1),limit:int = Query(default=2),payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    if not id:
        id = payload.get("id")
        # return f"{id}"
    followers = get_followers(db,id,page_no,limit)
    count = get_count_followers_and_following(db,id)
    return {"id":id,"total_Followers":count.get("Followers"),"followers":followers,"page_no":page_no,}


@router.get("/profile/following")
def get_all_following(id:Optional[str] = None,page_no:int = Query(default=1),limit:int = Query(default=2),payload:dict = Depends(verify_token),db:Session = Depends(database.get_db)):
    if not id:
        id = payload.get("id")
    followings = get_following(db,id,page_no,limit)
    count = get_count_followers_and_following(db,id)
    return {"id":id,"total_following":count.get("Followers"),"following":followings,"page_no":page_no}

@router.get("/profile/follow_count")
def get_count_fwr(id:Optional[str]=None,db:Session = Depends(database.get_db),payload:dict = Depends(verify_token)):
    if not id:
        id = payload.get("id")
    followers_count = get_count_followers_and_following(db,id)
    return {"user_id":id,"followers":followers_count.get("Followers"),"followings":followers_count.get("Following")}


