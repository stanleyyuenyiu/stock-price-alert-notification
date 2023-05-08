from xmlrpc.client import boolean
from pydantic import BaseModel
from datetime import datetime
import dataclasses

class Event(BaseModel):
    key:str
    payload: object
    created_at: int = int(datetime.utcnow().timestamp())
    version: int = 1

    class Config:
        orm_mode = True

@dataclasses.dataclass
class IdempotentConfig:
    enable:bool = False
    id_placement:str = "key"