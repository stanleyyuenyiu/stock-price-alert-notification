"""create rule table

Revision ID: 0696d2ce17a3
Revises: 154fbc22658f
Create Date: 2023-04-17 17:16:18.939115

"""
from alembic import op
from sqlalchemy import Column, String, Integer, Enum,Float, Boolean,  TIMESTAMP,text
from modules.rules.entities import utcnow,type_type,operator_type,unit_type
from sqlalchemy.types import DateTime
from modules.rules.models import EnumUnit, EnumType
# revision identifiers, used by Alembic.
revision = '0696d2ce17a3'
down_revision = '154fbc22658f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    type_type.create(op.get_bind(), checkfirst=True)
    operator_type.create(op.get_bind(), checkfirst=True)
    unit_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'rules',
        Column("rule_id", String, primary_key=True, index=True),
        Column("alert_id", String, nullable=False),
        Column("user_id", String, nullable=False),
        Column("type", type_type, nullable=False, default=EnumType.PRICE),
        Column("operator", operator_type, nullable=False),
        Column("unit", unit_type, nullable=False, default=EnumUnit.PECENT),
        Column("value", Float, nullable=False, default=0),
        Column("current", Float, nullable=False, default=0),
        Column("is_trigger", Boolean, nullable=False, default=False),
        Column("symbol", String, nullable=False),
        Column("created", DateTime(timezone=True), server_default=utcnow()),
        Column("updated", DateTime(timezone=True), onupdate=utcnow())
    )


def downgrade() -> None:
    op.drop_table('rules')
