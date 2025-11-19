"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create story_versions table
    op.create_table(
        'story_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('sources_snapshot', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('token_stats', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_story_versions_created_at'), 'story_versions', ['created_at'], unique=False)
    op.create_index(op.f('ix_story_versions_id'), 'story_versions', ['id'], unique=False)

    # Create feed_items table
    op.create_table(
        'feed_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_url', sa.String(), nullable=False),
        sa.Column('feed_name', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('link', sa.String(), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=False),
        sa.Column('raw', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash'),
        sa.UniqueConstraint('link', 'title', name='uix_link_title')
    )
    op.create_index(op.f('ix_feed_items_feed_url'), 'feed_items', ['feed_url'], unique=False)
    op.create_index(op.f('ix_feed_items_id'), 'feed_items', ['id'], unique=False)
    op.create_index(op.f('ix_feed_items_published_at'), 'feed_items', ['published_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feed_items_published_at'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_id'), table_name='feed_items')
    op.drop_index(op.f('ix_feed_items_feed_url'), table_name='feed_items')
    op.drop_table('feed_items')

    op.drop_index(op.f('ix_story_versions_id'), table_name='story_versions')
    op.drop_index(op.f('ix_story_versions_created_at'), table_name='story_versions')
    op.drop_table('story_versions')
