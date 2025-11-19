"""Add story_analytics table for sentiment, bias, fact-checking, and forecasting

Revision ID: 004
Revises: 003
Create Date: 2025-11-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create story_analytics table
    op.create_table(
        'story_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('story_version_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('overall_sentiment', sa.String(), nullable=True),
        sa.Column('sentiment_score', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bias_indicators', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bias_score', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('fact_checks', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('predictions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('events', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_story_analytics_id'), 'story_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_story_analytics_story_version_id'), 'story_analytics', ['story_version_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_story_analytics_story_version_id'), table_name='story_analytics')
    op.drop_index(op.f('ix_story_analytics_id'), table_name='story_analytics')
    op.drop_table('story_analytics')
