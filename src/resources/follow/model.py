from database.database import Base
from sqlalchemy import Column,String,ForeignKey,DateTime
from datetime import datetime,timezone
import uuid


class Follower(Base):
    __tablename__  = "followers"
    
    id = Column(String,primary_key= True,default=str(uuid.uuid4()))
    user_id = Column(String,ForeignKey('user.id'))
    follower_id = Column(String,ForeignKey('user.id'))
    created_at = Column(DateTime,default=datetime.now(tz=timezone.utc))