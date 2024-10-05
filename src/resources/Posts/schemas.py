from pydantic import *
from datetime import date, datetime
from typing import Optional


# class post_create(BaseModel):
#     data:bytes
#     captions:str = None
    
class post_update(BaseModel):
    data:str = None
    captions:str = None
    
class get_post(BaseModel):
    data:bytes
    captions:str
    likes:int

# class Image(BaseModel):
#     data: bytes              x
    
