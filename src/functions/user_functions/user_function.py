from config import key , algo, access_token_min, refresh_token_days ,otp_exp_time_min
from src.utils.hash import hash_password, verify_password
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.exc import NoResultFound , DataError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from src.resources.user.model import User,OTP
from src.resources.posts.model import Posts
from src.resources.likes.model import likes
import src.resources.user.schemas as schemas
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from dotenv import load_dotenv  
from random import randint
from pydantic import *
import os

load_dotenv() 
O_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# algo = os.getenv("algo")
# access_token_min = int(os.getenv("access_token_min"))
# refresh_token_days = int(os.getenv("refresh_token_days"))
# otp_exp_time_min= int(os.getenv("otp_exp_time_min"))



async def create_user(db: Session, user: schemas.Create_User):
    #checking the mobile number if it is valid or not
    if len(str(user.mobile_number))!=10:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Enter a valid mobile number!")
    try:
        is_mobile = (
            db.query(User).filter(User.mobile_number == user.mobile_number).first()
        )
    except Exception as err:
        pass
    if is_mobile:
        raise HTTPException(status_code=400, detail="Mobile number already exist!!")
    
    #checking the email if it is valid or not
    
    try:
        is_email = db.query(User).filter(User.email == user.email).first()
    except NoResultFound as err:
        print(str(err))
    if is_email:
        raise HTTPException(status_code=400, detail="Email already exist!!")

    #adding the user in database
    the_user = User(
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        email=user.email,
        birthdate=user.birthdate,
        password=hash_password(user.password),
    )
    
    try:
        db.add(the_user)
        db.commit()
        db.refresh(the_user)
    except DataError:
        raise HTTPException(status_code=406,detail="Please Enter a valid birthdate!")
    except Exception as err:
        raise HTTPException(status_code=404,detail=f"A Database error! {err}")
    
    # except 
    
    #creating an otp
    try:
        the_id = db.query(User).filter(User.email == user.email).one()
        the_otp = OTP(user_id=the_id.id, otp=randint(100000, 999999))
        db.add(the_otp)
        db.commit()
        db.refresh(the_otp)
    except Exception as err:
        raise HTTPException(status_code=404,detail="an database error")
    
    #Sending the otp
    conf = ConnectionConfig(
        MAIL_USERNAME="meetprajapati2074@gmail.com",
        MAIL_PASSWORD="nflu fxte aihg tbws",  
        MAIL_FROM="meetprajapati2074@gmail.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",  
        MAIL_STARTTLS=True,  
        MAIL_SSL_TLS=False,  
        USE_CREDENTIALS=True,
    )
    try:
        message = MessageSchema(
            subject="OTP",
            recipients=[user.email],
            body=f"{the_otp.otp}",
            subtype="html",
        )
        fm = FastMail(conf)
        await fm.send_message(message=message)
    except Exception as err:
        raise HTTPException(status_code=404, detail=f"{err}")
    


def verify_otp(otp_scheme: schemas.Create_User_Otp, db: Session):
    current_time = datetime.now()
    user_id = db.query(User).filter(User.email == otp_scheme.email).one().id
    data = db.query(OTP).filter(OTP.user_id == user_id).one()
    otp_create_time = data.created_at
    time_diff = otp_create_time + timedelta(minutes=otp_exp_time_min) 
    if current_time>time_diff:
        delete_otp(db,user_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="OTP expired!")
    otp2 = data.otp
    if otp_scheme.otp != otp2:
        return False
    return user_id


def delete_otp(db: Session, userid: str):
    try:
        result = db.query(OTP).filter(OTP.user_id == userid).delete()
        # if result == 0:
        #     raise HTTPException()
        db.commit()
        return True
    except NoResultFound as err:
        return err
    finally:
        return True


def create_token_once_expired(payload: dict):
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=access_token_min)
    payload.update({"exp": exp})
    token = jwt.encode(payload, key, algo)
    return token


def create_access_token_signup(user: schemas.Token_Schema):
    payload = dict(user)
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=access_token_min)
    # breakpoint()
    payload.update({"exp": exp,"type":"access"})
    token = jwt.encode(payload, key, algo)
    return token


def create_refresh_token(email: str, db: Session):
    data = db.query(User).filter(User.email == email).one()
    payload = {"name": data.first_name, "id": data.id}
    exp = datetime.now(tz=timezone.utc) + timedelta(days=refresh_token_days)
    payload.update({"exp": exp,"type":"refresh"})
    token = jwt.encode(payload, key, algo)
    return token


def token_decode(Token: str):
    data = jwt.decode(Token, key, algorithms=algo)
    return data


def access_token_create_login(email: str, db: Session):
    data = db.query(User).filter(User.email == email).one()
    payload = {"id": data.id, "name": data.first_name}
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=access_token_min)
    payload.update({"exp": exp,"type":"access"})
    token = jwt.encode(payload, key, algo)
    return token


def verify_token(token: str = Depends(O_scheme)):
    try:
        
        payload = token_decode(token)
        # print(payload)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: No payload in the token.",
            )
        # is_expired =  is_token_expired(payload)
        # if not is_expired:
        #     raise HTTPException(status_code=401,detail="Token expired!")
        return payload
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token!! {err}"
        )


def is_token_expired(payload: dict):
    current_time = datetime.now(tz=timezone.utc)

    payload_time = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    # breakpoint()
    if payload_time < current_time:
        return True
    return False


def get_user_data(db: Session, id: str):
    try:
        data = db.query(User).filter(User.id == id).one()
        print(data)
        return data
    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="User not found!")


def update_user_data(db: Session, updated_data: schemas.update_profile, id: str):
    if len(str(updated_data.mobile_number))!=10:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Enter a valid mobile number!")
    try:
        data = db.query(User).filter(User.id == id).first()
        if updated_data.first_name is not None:
            data.first_name = updated_data.first_name
        if updated_data.last_name is not None:
            data.last_name = updated_data.last_name
        if updated_data.mobile_number is not None:
            data.mobile_number = updated_data.mobile_number
        db.commit()

    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="User not found!")


def delete_user_data(db: Session, id: str):
    try:
        # db.query()
        data = db.query(User).filter(User.id == id).one()
        data.is_deleted = True
        db.commit()
    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="a database error!")


def get_hashed_pass(db: Session, email: str):
    data = db.query(User).filter(User.email == email).one_or_none()
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data.password


def user_login(db: Session, user: schemas.Login):
    data = db.query(User).filter(User.email == user.email).one_or_none()
    if data is None:
        raise HTTPException(status_code=404, detail="Invalid Email id!")
    hashed_pass = get_hashed_pass(db, user.email)
    if verify_password(user.password, hashed_pass):
        return True
    else:
        raise HTTPException(status_code=401, detail="Incorrect password!!")


def get_user_by_id(db: Session, userid: str):
    user = db.query(User).filter(User.id == userid).one()
    payload = {"name": user.first_name, "id": user.id}
    return payload


