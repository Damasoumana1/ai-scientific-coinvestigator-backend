"""add remote_id to research_paper

Revision ID: dc6a7b8c9d0e
Revises: 8a2d3e4f5b6c
Create Date: 2026-04-26 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dc6a7b8c9d0e'
down_revision: Union[str, None] = '8a2d3e4f5b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add remote_id and summary columns to research_papers table
    op.add_column('research_papers', sa.Column('remote_id', sa.Text(), nullable=True))
    op.add_column('research_papers', sa.Column('summary', sa.Text(), nullable=True))
    op.create_index(op.f('ix_research_papers_remote_id'), 'research_papers', ['remote_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_research_papers_remote_id'), table_name='research_papers')
    op.drop_column('research_papers', 'summary')
    op.drop_column('research_papers', 'remote_id')
