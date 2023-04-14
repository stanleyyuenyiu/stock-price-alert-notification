from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


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
    is_trigger:bool = False
    symbol:str = ""

class RuleModel(RuleDocModel):
    rule_id: str = ""
    alert_id: str = ""
    user_id: str = ""
    type: str = "PIC"
    operator: str = ""


