"""remove-unnecessary-columns

Revision ID: 9068d50bc5be
Revises: 74e741a84227
Create Date: 2025-05-30 19:43:41.432814

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9068d50bc5be"
down_revision: Union[str, None] = "74e741a84227"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "gender")
    op.drop_column("users", "birthday")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("birthday", sa.DATE(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "users",
        sa.Column("gender", sa.VARCHAR(length=6), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###
