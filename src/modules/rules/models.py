from __future__ import annotations
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, validator


class EnumOperator(Enum):
    GTE = "gte"
    LTE = "lte"

class EnumUnit(Enum):
    NUMBER = "N"
    PECENT = "P"

class EnumType(Enum):
    PRICE = "PIC"
    VOL = "VOL"


class RuleDocModel(BaseModel):
    value:float = 0
    current:float = 0
    is_trigger:bool = False
    symbol:str = ""

class RuleModel(RuleDocModel):
    rule_id: str = ""
    alert_id: str = ""
    user_id: str = ""
    type: EnumType = EnumType.PRICE
    unit: EnumUnit = EnumUnit.NUMBER
    operator: Optional[EnumOperator] = None
    
    class Config:
        orm_mode = True

class APIRequest(BaseModel):
    @validator('value' , check_fields=False)
    def non_zero(cls, v):
        if v <= 0:
            raise ValueError('value must greater than 0')
        return float(v)

class APIUpdateRequest(APIRequest):
    alert_id: Optional[str]
    type: Optional[EnumType] = EnumType.PRICE
    unit: EnumUnit = EnumUnit.NUMBER
    operator: Optional[EnumOperator]
    value:Optional[float]
    current:Optional[float]

class APIAddRequest(APIRequest):
    alert_id: str
    user_id: str
    type: EnumType = EnumType.PRICE
    unit: EnumUnit = EnumUnit.NUMBER
    operator: EnumOperator
    value: float
    current:float = 0
    symbol: str

class APIGeneralResponse(BaseModel):
    data: Optional[RuleModel]
    status: bool = True
    error: Optional[List[object]]

class APIErrorResponse(APIGeneralResponse):
    message: str