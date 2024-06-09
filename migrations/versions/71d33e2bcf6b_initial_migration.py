"""Initial migration

Revision ID: 71d33e2bcf6b
Revises: c3811fc0bc6c
Create Date: 2024-05-20 19:10:06.132345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '71d33e2bcf6b'
down_revision: Union[str, None] = 'c3811fc0bc6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_name', mysql.VARCHAR(length=120), nullable=False))
    # ### end Alembic commands ###
