from sqlalchemy import *
from Database.database import Base
import uuid
from datetime import datetime , timezone

def create_uuid():
    return str(uuid.uuid4())


class likes(Base):
    __tablename__  = "likes"
    
    id = Column(String, primary_key=True, default=create_uuid())
    post_id = Column(String,ForeignKey('posts.id'))
    user_id = Column(String,ForeignKey('user.id'))
    liked_at = Column(DateTime,default=datetime.now(tz=timezone.utc))
    unliked_at = Column(DateTime,default=datetime.now(tz=timezone.utc))