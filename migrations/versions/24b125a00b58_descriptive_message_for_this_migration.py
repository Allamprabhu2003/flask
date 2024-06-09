"""Descriptive message for this migration

Revision ID: 24b125a00b58
Revises: 71d33e2bcf6b
Create Date: 2024-05-25 11:36:53.175721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24b125a00b58'
down_revision: Union[str, None] = '71d33e2bcf6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
