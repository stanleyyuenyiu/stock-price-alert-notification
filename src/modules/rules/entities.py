from venv import create
from lib.database.entities import Base
from sqlalchemy import Column, String, Integer, Enum,Float, Boolean,  TIMESTAMP,text
from sqlalchemy.sql import func, expression
from .models import EnumOperator, EnumUnit, EnumType, EnumStatus
from sqlalchemy.types import DateTime
from sqlalchemy.ext.compiler import compiles

class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

operator_type: Enum = Enum(
    EnumOperator,
    name="operator_type",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

unit_type: Enum = Enum(
    EnumUnit,
    name="unit_type",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

type_type: Enum = Enum(
    EnumType,
    name="type_type",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

status_type: Enum = Enum(
    EnumStatus,
    name="status_type",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

class RuleEntity(Base):
    __tablename__ = "rules"
    rule_id     =   Column(String, primary_key=True, index=True)
    alert_id    =   Column(String, nullable=False)
    user_id     =   Column(String, nullable=False)
    type        =   Column("type", type_type, nullable=False, default=EnumType.PRICE)
    operator    =   Column("operator",operator_type, nullable=False)
    unit        =   Column("unit",unit_type, nullable=False, default=EnumUnit.NUMBER)
    value       =   Column(Float, nullable=False, default=0)
    current     =   Column(Float, nullable=False, default=0)
    status      =   Column("status",status_type, nullable=False, default=EnumStatus.NEW)
    symbol      =   Column(String, nullable=False)
    created     =   Column(DateTime(timezone=True), nullable=True, server_default=utcnow(), default=utcnow())
    updated     =   Column(DateTime(timezone=True), nullable=True)
