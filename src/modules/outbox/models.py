from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from abc import ABC
from lib.utils.hashing import consistent_hash
import uuid

class Event(BaseModel):
    key:str
    payload: object
    created_at: int = int(datetime.utcnow().timestamp())
    version: int = 1


class BaseEvent(ABC):
    _timestamp:int = 0
    _partition:int = -1
    _payload:str = ""
    _aggregate_id:str = ""
    _id:str = ""
    
    def __init__(self, id, payload:dict) -> None:
        self.aggregate_id = id
        self.payload = payload
    
    @classmethod
    def of(cls, model:BaseModel):
        return cls(id="", payload=model)

    @property
    def id(self) -> str:
        if not self._id:
            self._id = uuid.uuid4()
        return self._id

    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id
    
    @aggregate_id.setter
    def aggregate_id(self, val:str):
        self._aggregate_id = val
        self._partition = consistent_hash(self._aggregate_id, 50)

    @property
    def aggregate_type(self) -> str:
        return "";
    
    @property
    def payload(self) -> str:
        return self._payload;
    
    @payload.setter
    def payload(self, value:Optional[BaseModel]):
        self._payload = Event(
            key = self.aggregate_id,
            payload = value
        ).json()

    @property
    def type(self) -> str:
        return "";

    @property
    def timestamp(self) -> int:
        if not self._timestamp:
            self._timestamp = int(datetime.utcnow().timestamp())
        return self._timestamp

    @property
    def version(self) -> str:
        return "1";

    @property
    def partition(self) -> str:
        return self._partition

    class Config:
        orm_mode = True