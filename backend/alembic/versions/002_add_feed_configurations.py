"""Add feed_configurations table

Revision ID: 002
Revises: 001
Create Date: 2025-11-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create feed_configurations table
    op.create_table(
        'feed_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_fetched', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fetch_error', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feed_configurations_id'), 'feed_configurations', ['id'], unique=False)
    op.create_index(op.f('ix_feed_configurations_url'), 'feed_configurations', ['url'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_feed_configurations_url'), table_name='feed_configurations')
    op.drop_index(op.f('ix_feed_configurations_id'), table_name='feed_configurations')
    op.drop_table('feed_configurations')
