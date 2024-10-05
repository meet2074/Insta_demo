from sqlalchemy import *
from database.database import Base
import uuid
from datetime import datetime , timezone

def create_uuid():
    return str(uuid.uuid4())


class Posts(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True, default=create_uuid)
    user_id = Column(String,ForeignKey('user.id'))
    data = Column(LargeBinary, nullable=False)
    likes = Column(Integer,default=0)
    captions = Column(String)
    created_at = Column(DateTime,default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime,default=datetime.now(tz=timezone.utc))    
    is_deleted = Column(Boolean,default=False)
    
class Image(Base):
    __tablename__ = "image"
    
    id = Column(String, primary_key=True)
    image = Column(LargeBinary,nullable=True)

