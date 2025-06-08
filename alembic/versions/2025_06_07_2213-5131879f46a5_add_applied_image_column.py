"""add applied_image column

Revision ID: 5131879f46a5
Revises: d04f58b299b4
Create Date: 2025-06-07 22:13:25.119763

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5131879f46a5"
down_revision: Union[str, None] = "d04f58b299b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "store_items",
        "image_url",
        existing_type=sa.VARCHAR(length=200),
        nullable=False,
        new_column_name="item_image_url",
        existing_nullable=True,
    )
    op.add_column(
        "store_items",
        sa.Column(
            "applied_image_url",
            sa.String(length=200),
            nullable=False,
            server_default="",
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "store_items",
        "item_image_url",
        existing_type=sa.VARCHAR(length=200),
        nullable=True,
        new_column_name="image_url",
        existing_nullable=False,
    )
    op.drop_column("store_items", "applied_image_url")
    # ### end Alembic commands ###
