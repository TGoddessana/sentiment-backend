"""change equipped item columns

Revision ID: d04f58b299b4
Revises: fc363d3eaec6
Create Date: 2025-06-04 14:31:33.655406

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d04f58b299b4"
down_revision: Union[str, None] = "fc363d3eaec6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_items",
        sa.Column(
            "equipped", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.drop_constraint(
        op.f("users_equipped_background_id_fkey"), "users", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("users_equipped_accessory_id_fkey"), "users", type_="foreignkey"
    )
    op.drop_column("users", "equipped_background_id")
    op.drop_column("users", "equipped_accessory_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "equipped_accessory_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "equipped_background_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        op.f("users_equipped_accessory_id_fkey"),
        "users",
        "store_items",
        ["equipped_accessory_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("users_equipped_background_id_fkey"),
        "users",
        "store_items",
        ["equipped_background_id"],
        ["id"],
    )
    op.drop_column("user_items", "equipped")
    # ### end Alembic commands ###
