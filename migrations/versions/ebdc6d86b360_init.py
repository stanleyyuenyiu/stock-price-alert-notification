"""init

Revision ID: ebdc6d86b360
Revises: 
Create Date: 2023-04-03 15:54:37.517370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebdc6d86b360'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'outbox_event_search_alert',
        sa.Column('id', sa.String(200), primary_key=True),
        sa.Column('data', sa.String(500), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(200), nullable=False),
    )
    

def downgrade() -> None:
    op.drop_table('outbox_event_search_alert')

