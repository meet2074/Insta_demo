from sqlalchemy import *
from database.database import Base
import uuid
from datetime import datetime , timezone



class likes(Base):
    __tablename__  = "likes"
    
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    post_id = Column(String,ForeignKey('posts.id'))
    user_id = Column(String,ForeignKey('user.id'))