"""create analyzed_emotion column

Revision ID: 74e741a84227
Revises: 49842c2d21a0
Create Date: 2025-05-29 23:22:56.355987

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "74e741a84227"
down_revision: Union[str, None] = "49842c2d21a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "diaries", sa.Column("analyzed_emotion", sa.String(length=10), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("diaries", "analyzed_emotion")
    # ### end Alembic commands ###
