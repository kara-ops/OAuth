"""Session table rename to UserSession

Revision ID: f8a3e74c88bd
Revises: c751c0b7cd18
Create Date: 2026-07-10 20:22:52.016859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a3e74c88bd'
down_revision: Union[str, Sequence[str], None] = 'c751c0b7cd18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename Sesion table to UserSession
    op.rename_table('Session', 'UserSession')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Rename table UserSession to Session
    op.rename_table('UserSession', 'Session')
    # ### end Alembic commands ###
