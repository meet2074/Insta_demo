from pydantic import *
from datetime import date, datetime
from typing import Optional


class Create_User(BaseModel):
    first_name: str
    middle_name: str = None
    last_name: str
    mobile_number: int
    email: EmailStr
    birthdate: str
    password: str


class Create_User_Otp(BaseModel):
    email: EmailStr
    otp: int


class Token_Schema(BaseModel):
    first_name: str
    userid: int


class get_profile_response(BaseModel):
    first_name: str
    last_name: str
    birthdate: date
    email: EmailStr = None


class update_profile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile_number: Optional[int] = None


class Login(BaseModel):
    email: EmailStr
    password: str


class EmailSchema(BaseModel):
    email: EmailStr
    Otp: int
