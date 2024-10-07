from pydantic import BaseModel
from datetime import datetime

class AllCommnetsRespons(BaseModel):
    userid: str
    data : str
    created_at :datetime
    
class CreateComment(BaseModel):
    comment:str