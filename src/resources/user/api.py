from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import database
from . import schemas
from src.functions.user_functions.user_function import *

router = APIRouter()

@router.post("/sign_up")
async def user_create(user: schemas.Create_User, db: Session = Depends(database.get_db)):
    await create_user(db,user)
    return f"Otp sent successfully on {user.email}!"

@router.post("/verify_otp")
def check_otp(data: schemas.Create_User_Otp, db: Session = Depends(database.get_db)):
    is_correct = verify_otp(data, db)   
    if is_correct:
        delete_otp(db, is_correct)
        payload = get_user_by_id(db, is_correct)
        token = create_access_token_signup(payload)
        refresh_token = create_refresh_token(data.email,db)
        return {"message": "Account created Successfully!! ", "access token": token,"refresh token":refresh_token}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect Otp!")


@router.get("/profile", response_model=schemas.get_profile_response)
def get_posts(
    payload: dict = Depends(verify_token), db: Session = Depends(database.get_db)
):
    is_expired = is_token_expired(payload)
    # breakpoint()
    if not is_expired:
        id = payload.get("id")
        posts = get_user_data(db, id)
        return posts
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )

@router.put("/update")
def update_data(
    update_scheme: schemas.update_profile,
    payload: dict = Depends(verify_token),
    db: Session = Depends(database.get_db),
):
    is_expired = is_token_expired(payload)
    print(is_expired)
    if not is_expired:
        id = payload.get("id")
        update_user_data(db, update_scheme, id)
        return "Updated Successfully!!"
    else:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )


@router.delete("/delete")
def delete_data(
    payload: dict = Depends(verify_token), db: Session = Depends(database.get_db)
):
    id = payload.get("id")
    delete_user_data(db, id)
    return "Deleted successfully!!"


@router.post("/login")
def login(user: schemas.Login, db: Session = Depends(database.get_db)):
    login = user_login(db, user)
    if login:
        access_token = access_token_create_login(user.email, db)
        refresh_token = create_refresh_token(user.email,db)
    return {"access token": access_token, "Refresh token": refresh_token}


@router.get("/refresh")
def refresh_token(payload: dict = Depends(verify_token)):

    is_expired = is_token_expired(payload)
    if is_expired:
        token = create_token_once_expired(payload)
        return {"new access token": token}
    else:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not expired!"
        )
