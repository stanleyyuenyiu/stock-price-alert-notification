from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    key:str
    payload: object
    created_at: int = int(datetime.utcnow().timestamp())
    version: int = 1

    class Config:
        orm_mode = True
