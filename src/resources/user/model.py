from sqlalchemy import *
from database.database import Base
import uuid
from datetime import datetime , timezone


class User(Base):   
    __tablename__ = "user"

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    middle_name = Column(String,nullable=True)
    last_name = Column(String,nullable=False)
    mobile_number = Column(BigInteger,unique = True,nullable=False)
    email = Column(String, unique=True , nullable=False)
    birthdate = Column(Date,nullable=False)
    password = Column(String,nullable=False)
    followers = Column(Integer,default=0)
    following = Column(Integer,default=0)
    posts = Column(Integer,default=0)
    created_at = Column(DateTime,default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime,default=datetime.now(tz=timezone.utc))
    is_deleted = Column(Boolean,nullable=True,default=False)
    is_active = Column(Boolean,default=False)
    is_not_active = Column(Boolean,default=True)


class OTP(Base):
    __tablename__ = "otp"
    
    id = Column(String, primary_key=True,default=str(uuid.uuid4()))
    user_id = Column(String,ForeignKey('user.id'),unique=False)
    otp = Column(Integer)
    created_at = Column(DateTime,default=datetime.now(tz=timezone.utc))
    updateed_at = Column(DateTime,default=datetime.now(tz=timezone.utc)) 
    
     
      
         
    