"""Add opt-in tourist marker. Existing users are ordinary users.

Revision ID: 62c5e0a9b441
Revises: ede4ba9c2dfe
"""

from alembic import op
import sqlalchemy as sa

revision = "62c5e0a9b441"
down_revision = "ede4ba9c2dfe"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_tourist", sa.Boolean(), nullable=False, server_default="0"
            )
        )


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("is_tourist")
