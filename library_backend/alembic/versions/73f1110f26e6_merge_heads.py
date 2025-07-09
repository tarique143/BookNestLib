"""merge heads

Revision ID: 73f1110f26e6
Revises: 79d93c885cd5, c74bbeb0ef20
Create Date: 2025-07-09 21:52:52.745241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73f1110f26e6'
down_revision: Union[str, Sequence[str], None] = ('79d93c885cd5', 'c74bbeb0ef20')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
