from src.config import Env
from src.utils.hash import hash_password, verify_password
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.exc import NoResultFound , DataError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from src.resources.user.model import User,OTP
import src.resources.user.schemas as schemas
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from dotenv import load_dotenv  
from random import randint
from pydantic import *
import uuid

load_dotenv() 
O_scheme = OAuth2PasswordBearer(tokenUrl="/token")
access_token_min = 300
refresh_token_days = 7
otp_exp_time_min= 100




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
        if is_mobile.is_deleted:
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
        id=str(uuid.uuid4()),
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
        MAIL_USERNAME=Env.MAIL_USERNAME,
        MAIL_PASSWORD=Env.MAIL_PASSWORD,  
        MAIL_FROM=Env.MAIL_USERNAME,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",  
        MAIL_STARTTLS=True,  
        MAIL_SSL_TLS=False,  
        USE_CREDENTIALS=True,
    )
    # the_otp = randint(100000,999999)
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
    
    # return {"the_user":the_user,"otp":the_otp}


def verify_otp(otp_scheme: schemas.Create_User_Otp, db: Session):
    
    current_time = datetime.now()
    user_id = db.query(User).filter(User.email == otp_scheme.email).one_or_none().id
    data = db.query(OTP).filter(OTP.user_id == user_id).one_or_none()
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
        db.query(OTP).filter(OTP.user_id == userid).delete()
        # if result == 0:
        #     raise HTTPException()
        db.commit()
        return True
    except NoResultFound as err:
        return err

# def create_access_token(payload:dict,db:Session):
#     exp = datetime.now(tz=timezone.utc) + timedelta(minutes=access_token_min)
#     payload.update({"exp": exp,"type":"access"})
#     token = jwt.encode(payload, key, algo)
#     return token


def create_refresh_token(email: str, db: Session):
    data = db.query(User).filter(User.email == email).one()
    payload = {"name": data.first_name, "id": data.id}
    exp = datetime.now(tz=timezone.utc) + timedelta(days=refresh_token_days)
    payload.update({"exp": exp,"type":"refresh"})
    token = jwt.encode(payload, Env.key, Env.algo)
    return token



def access_token_create_login(email: str, db: Session):
    data = db.query(User).filter(User.email == email).one()
    payload = {"id": data.id, "name": data.first_name}
    exp = datetime.now(tz=timezone.utc) + timedelta(hours=access_token_min)
    payload.update({"exp": exp,"type":"access"})
    token = jwt.encode(payload, Env.key, Env.algo)
    return token


def verify_token(token: str = Depends(O_scheme)):
    try:
        
        payload = jwt.decode(token, Env.key, algorithms=Env.algo)
        # print(payload)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: No payload in the token.",
            )
        return payload
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token!! {err}"
        )
def get_all_user_data(db:Session,page:int,limit:int):
    page = page*limit-limit
    data = db.query(User).offset(page).limit(limit).all()
    return data


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
        data.updated_at = datetime.now(tz=timezone.utc)
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


def user_login(db: Session, user: schemas.Login):
    data = db.query(User).filter(User.email == user.email).one_or_none()
    
    if data is None or data.is_deleted:
        raise HTTPException(status_code=404, detail="Invalid Email id!")
    is_otp = db.query(OTP).filter(OTP.user_id==data.id).one_or_none()
    if is_otp:
        raise HTTPException(status_code=401,detail="Please verify the otp")   
    hashed_pass = data.password
    if verify_password(user.password, hashed_pass):
        data.is_active = True
        return True
    else:
        raise HTTPException(status_code=401, detail="Incorrect password!!")


def get_user_by_id(db: Session, userid: str):
    user = db.query(User).filter(User.id == userid).one()
    payload = {"name": user.first_name, "id": user.id}
    return payload
