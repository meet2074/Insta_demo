from sqlalchemy import *
from database.database import Base
import uuid
from datetime import datetime , timezone

class Save(Base):
    __tablename__ = "save"
    
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    postid = Column(String,ForeignKey("posts.id"),nullable=False,unique=False)
    userid = Column(String, ForeignKey("user.id"),nullable=False,unique=False)
    created_at = Column(String,default=datetime.now(tz=timezone.utc))