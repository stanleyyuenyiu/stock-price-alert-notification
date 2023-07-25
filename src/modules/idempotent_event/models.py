from pydantic import BaseModel

class IdempotentEventModel(BaseModel):
    event_id:str
    group_id:str
    
    class Config:
        orm_mode = True
