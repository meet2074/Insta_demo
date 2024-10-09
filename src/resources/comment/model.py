from sqlalchemy import *
from database.database import Base
import uuid
from datetime import datetime , timezone

class Comments(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True,default=str(uuid.uuid4()))
    postid = Column(String,ForeignKey("posts.id"),nullable=False,unique=False)
    userid = Column(String, ForeignKey("user.id"),nullable=False,unique=False)
    data = Column(String,nullable=False,unique=False)
    replies = Column(Integer,nullable=True,default=0)
    created_at = Column(String,default=datetime.now(tz=timezone.utc))
    is_deleted = Column(Boolean,default=False)
    
class MetaComments(Base):
    __tablename__ = "metacomments"
    
    id = Column(String, primary_key=True,default=str(uuid.uuid4()))
    commentid = Column(String,ForeignKey("comments.id"),nullable=False,unique=False)
    userid = Column(String, ForeignKey("user.id"),nullable=False,unique=False)
    data = Column(String,nullable=False,unique=False)
    created_at = Column(String,default=datetime.now(tz=timezone.utc))
    is_deleted = Column(Boolean,default=False)
    