from pydantic import *
from datetime import date, datetime
from typing import Optional


class post_create(BaseModel):
    data:str
    captions:str = None
    
class post_update(BaseModel):
    data:str = None
    captions:str = None
    
class get_post(BaseModel):
    data:str
    captions:str
    likes:int
    
