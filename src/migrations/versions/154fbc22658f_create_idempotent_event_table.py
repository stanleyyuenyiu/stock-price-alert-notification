"""create idempotent event table

Revision ID: 154fbc22658f
Revises: ebdc6d86b360
Create Date: 2023-04-13 16:32:49.560660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '154fbc22658f'
down_revision = 'ebdc6d86b360'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'idempotent_event',
        sa.Column('event_id', sa.String(200)),
        sa.Column('group_id', sa.String(200))
    )
    op.create_primary_key("pk_idempotent_event", "idempotent_event", ["event_id", "group_id"])


def downgrade() -> None:
    op.drop_table('idempotent_event')
