"""Add hashed_password to user

Revision ID: 8a2d3e4f5b6c
Revises: 73d647d8385f
Create Date: 2026-03-20 23:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a2d3e4f5b6c'
down_revision: Union[str, None] = '73d647d8385f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hashed_password column to users table
    # We make it nullable=True initially to support existing users, 
    # but the application logic will require it for new users.
    op.add_column('users', sa.Column('hashed_password', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'hashed_password')
