from __future__ import annotations
from enum import Enum
from typing import Generic, Optional, List, TypeVar, Union
from pydantic import BaseModel, validator
from pydantic.generics import GenericModel


class MesaageTemplateModel(BaseModel):
    value:float = 0
    current:float = 0
    is_trigger:bool = False
    symbol:str = ""

class MesaageLangModel(BaseModel):
    value:float = 0
    current:float = 0
    symbol:str = ""
    rule_id: str = ""
    alert_id: str = ""
    user_id: str = ""
    type: EnumType = EnumType.PRICE
    unit: EnumUnit = EnumUnit.NUMBER
    operator: Optional[EnumOperator] = None
    status: EnumStatus = EnumStatus.NEW
    
    class Config:
        orm_mode = True
