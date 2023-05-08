"""init

Revision ID: ebdc6d86b360
Revises: 
Create Date: 2023-04-03 15:54:37.517370

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import TIMESTAMP, UUID

# revision identifiers, used by Alembic.
revision = 'ebdc6d86b360'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'outbox',
        sa.Column('id', UUID(True), primary_key=True),
        sa.Column('aggregatetype', sa.String(500), nullable=False),
        sa.Column('aggregateid', sa.String(200), nullable=False),
        sa.Column('type', sa.String(200), nullable=False),
        sa.Column('payload', sa.String(4096), nullable=False),
        sa.Column("timestamp", sa.Integer(), nullable=False),
        sa.Column('version', sa.String(10), nullable=False),
    
    )
    

def downgrade() -> None:
    op.drop_table('outbox')

